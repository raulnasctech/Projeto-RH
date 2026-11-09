import unittest
from unittest.mock import patch

import httpx

from Gestao_RH_Impacta import department_service


class FakeAsyncClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False

    async def get(self, url, **kwargs):
        self.calls.append(("get", url, kwargs))
        if isinstance(self.response, Exception):
            raise self.response
        return self.response

    async def post(self, url, **kwargs):
        self.calls.append(("post", url, kwargs))
        if isinstance(self.response, Exception):
            raise self.response
        return self.response

    async def patch(self, url, **kwargs):
        self.calls.append(("patch", url, kwargs))
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


class DepartmentServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_lists_departments_with_auth_and_normalized_names(self):
        client = FakeAsyncClient(
            httpx.Response(
                200,
                json=[
                    {"id": 3, "name": "Produto"},
                    {"id": "8", "nome": "Engenharia"},
                ],
            )
        )
        with patch.object(
            department_service.httpx, "AsyncClient", return_value=client
        ):
            departments = await department_service.list_departments(
                "https://example.xano.io/api:rh/", "fixture-token"
            )

        self.assertEqual(
            departments,
            [
                {"id": "3", "name": "Produto"},
                {"id": "8", "name": "Engenharia"},
            ],
        )
        self.assertEqual(client.calls[0][1], "https://example.xano.io/api:rh/departments")
        self.assertEqual(
            client.calls[0][2]["headers"]["Authorization"],
            "Bearer fixture-token",
        )

    async def test_rejects_invalid_list_shapes_instead_of_showing_empty_state(self):
        for payload in ({"items": []}, [None], [{"id": 1}], [{"id": 0, "name": "RH"}]):
            client = FakeAsyncClient(httpx.Response(200, json=payload))
            with (
                self.subTest(payload=payload),
                patch.object(
                    department_service.httpx, "AsyncClient", return_value=client
                ),
                self.assertRaises(department_service.DepartmentError),
            ):
                await department_service.list_departments(
                    "https://example.xano.io/api:rh", "fixture-token"
                )

    async def test_reports_unauthorized_department_requests(self):
        client = FakeAsyncClient(
            httpx.Response(403, json={"message": "Forbidden"})
        )
        with (
            patch.object(
                department_service.httpx, "AsyncClient", return_value=client
            ),
            self.assertRaises(department_service.DepartmentAccessDenied),
        ):
            await department_service.list_departments(
                "https://example.xano.io/api:rh", "fixture-token"
            )

    async def test_creates_department_with_trimmed_name_and_validates_id(self):
        client = FakeAsyncClient(httpx.Response(200, json={"id": 12, "name": "RH"}))
        with patch.object(
            department_service.httpx, "AsyncClient", return_value=client
        ):
            department_id = await department_service.create_department(
                "https://example.xano.io/api:rh", "fixture-token", "  RH  "
            )

        self.assertEqual(department_id, 12)
        self.assertEqual(
            client.calls[0][2]["json"],
            {"nome": "RH"},
        )
        self.assertEqual(
            client.calls[0][2]["headers"]["Authorization"],
            "Bearer fixture-token",
        )

    async def test_rejects_create_response_without_a_valid_id(self):
        client = FakeAsyncClient(httpx.Response(200, json={"name": "RH"}))
        with (
            patch.object(
                department_service.httpx, "AsyncClient", return_value=client
            ),
            self.assertRaises(department_service.DepartmentError),
        ):
            await department_service.create_department(
                "https://example.xano.io/api:rh", "fixture-token", "RH"
            )

    async def test_create_error_does_not_expose_backend_response_body(self):
        response_body = "Invalid name: sensitive-backend-detail"
        client = FakeAsyncClient(
            httpx.Response(500, json={"message": response_body})
        )
        with patch.object(
            department_service.httpx, "AsyncClient", return_value=client
        ):
            with self.assertRaises(department_service.DepartmentError) as context:
                await department_service.create_department(
                    "https://example.xano.io/api:rh", "fixture-token", "RH"
                )

        self.assertIn("HTTP 500", str(context.exception))
        self.assertNotIn(response_body, str(context.exception))

    async def test_updates_department_with_authorization_and_trimmed_name(self):
        client = FakeAsyncClient(httpx.Response(200, json={"id": 12, "name": "RH"}))
        with patch.object(
            department_service.httpx, "AsyncClient", return_value=client
        ):
            await department_service.update_department(
                "https://example.xano.io/api:rh",
                "fixture-token",
                "12",
                "  Recursos Humanos  ",
            )

        self.assertEqual(
            client.calls[0][1],
            "https://example.xano.io/api:rh/departments/12",
        )
        self.assertEqual(
            client.calls[0][2]["json"],
            {"nome": "Recursos Humanos"},
        )
        self.assertEqual(
            client.calls[0][2]["headers"]["Authorization"],
            "Bearer fixture-token",
        )

    async def test_rejects_invalid_update_ids(self):
        client = FakeAsyncClient(httpx.Response(200, json={}))
        with (
            patch.object(
                department_service.httpx, "AsyncClient", return_value=client
            ),
            self.assertRaises(department_service.DepartmentError),
        ):
            await department_service.update_department(
                "https://example.xano.io/api:rh", "fixture-token", "0", "RH"
            )
        self.assertEqual(client.calls, [])


if __name__ == "__main__":
    unittest.main()
