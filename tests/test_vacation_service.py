import unittest
from datetime import date
from unittest.mock import patch

import httpx

from Gestao_RH_Impacta import vacation_service
from Gestao_RH_Impacta.vacation_service import VacationRequest


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


class VacationServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_lists_vacation_requests_with_auth_and_parsed_fields(self):
        client = FakeAsyncClient(
            httpx.Response(
                200,
                json=[
                    {
                        "id": 8,
                        "employees_id": 3,
                        "employee_name": "Ana Souza",
                        "start_date": "2026-11-07",
                        "end_date": "2026-11-20",
                        "status": "Pendente",
                    }
                ],
            )
        )
        with patch.object(
            vacation_service.httpx, "AsyncClient", return_value=client
        ):
            requests = await vacation_service.list_vacation_requests(
                "https://example.xano.io/api:rh/", "fixture-token"
            )

        self.assertEqual(
            requests[0].as_dict(),
            {
                "id": "8",
                "employee_id": "3",
                "employee_name": "Ana Souza",
                "start_date": "2026-11-07",
                "end_date": "2026-11-20",
                "status": "Pendente",
            },
        )
        self.assertEqual(
            client.calls[0][1],
            "https://example.xano.io/api:rh/vacation_requests",
        )
        self.assertEqual(
            client.calls[0][2]["headers"]["Authorization"],
            "Bearer fixture-token",
        )

    async def test_rejects_malformed_list_and_record_data(self):
        payloads = (
            {"items": []},
            [None],
            [{"id": 0}],
            [
                {
                    "id": 2,
                    "employees_id": 1,
                    "start_date": "2026-11-10",
                    "end_date": "2026-11-09",
                    "status": "Pendente",
                }
            ],
            [
                {
                    "id": 2,
                    "employees_id": 1,
                    "start_date": "2026-11-09",
                    "end_date": "2026-11-10",
                    "status": "Removida",
                }
            ],
        )
        for payload in payloads:
            client = FakeAsyncClient(httpx.Response(200, json=payload))
            with (
                self.subTest(payload=payload),
                patch.object(
                    vacation_service.httpx, "AsyncClient", return_value=client
                ),
                self.assertRaises(vacation_service.VacationRequestError),
            ):
                await vacation_service.list_vacation_requests(
                    "https://example.xano.io/api:rh", "fixture-token"
                )

    async def test_reports_unauthorized_requests_without_exposing_backend_body(
        self,
    ):
        client = FakeAsyncClient(
            httpx.Response(
                403,
                json={"message": "secret authorization implementation detail"},
            )
        )
        with (
            patch.object(
                vacation_service.httpx, "AsyncClient", return_value=client
            ),
            self.assertRaises(vacation_service.VacationAccessDenied),
        ):
            await vacation_service.list_vacation_requests(
                "https://example.xano.io/api:rh", "fixture-token"
            )

    async def test_creates_request_with_expected_payload(self):
        client = FakeAsyncClient(httpx.Response(200, json={"id": 15}))
        with patch.object(
            vacation_service.httpx, "AsyncClient", return_value=client
        ):
            request_id = await vacation_service.create_vacation_request(
                "https://example.xano.io/api:rh",
                "fixture-token",
                "4",
                "2026-12-01",
                "2026-12-10",
            )

        self.assertEqual(request_id, "15")
        self.assertEqual(
            client.calls[0][2]["json"],
            {
                "employees_id": 4,
                "start_date": "2026-12-01",
                "end_date": "2026-12-10",
            },
        )
        self.assertNotIn("status", client.calls[0][2]["json"])
        self.assertNotIn("decided_by", client.calls[0][2]["json"])

    async def test_rejects_invalid_create_fields_before_request(self):
        client = FakeAsyncClient(httpx.Response(200, json={"id": 1}))
        with (
            patch.object(
                vacation_service.httpx, "AsyncClient", return_value=client
            ),
            self.assertRaises(vacation_service.VacationRequestError),
        ):
            await vacation_service.create_vacation_request(
                "https://example.xano.io/api:rh",
                "fixture-token",
                "1",
                "2026-12-11",
                "2026-12-10",
            )
        self.assertEqual(client.calls, [])

    async def test_decides_pending_request_with_allowlisted_status(self):
        client = FakeAsyncClient(
            httpx.Response(200, json={"id": 7, "status": "Aprovada"})
        )
        with patch.object(
            vacation_service.httpx, "AsyncClient", return_value=client
        ):
            await vacation_service.decide_vacation_request(
                "https://example.xano.io/api:rh",
                "fixture-token",
                "7",
                "Aprovada",
            )

        self.assertEqual(
            client.calls[0][1],
            "https://example.xano.io/api:rh/vacation_requests/7",
        )
        self.assertEqual(client.calls[0][2]["json"], {"status": "Aprovada"})

    async def test_rejects_invalid_decision_and_confirmation(self):
        client = FakeAsyncClient(
            httpx.Response(200, json={"id": 7, "status": "Pendente"})
        )
        with (
            patch.object(
                vacation_service.httpx, "AsyncClient", return_value=client
            ),
            self.assertRaises(vacation_service.VacationRequestError),
        ):
            await vacation_service.decide_vacation_request(
                "https://example.xano.io/api:rh",
                "fixture-token",
                "7",
                "Pendente",
            )
        self.assertEqual(client.calls, [])

    def test_counts_distinct_employees_with_current_approved_requests(self):
        requests = [
            VacationRequest("1", "3", "Ana", "2026-11-07", "2026-11-10", "Aprovada"),
            VacationRequest("2", "3", "Ana", "2026-11-07", "2026-11-09", "Aprovada"),
            VacationRequest("3", "4", "Bia", "2026-11-08", "2026-11-12", "Pendente"),
            VacationRequest("4", "5", "Caio", "2026-11-06", "2026-11-06", "Aprovada"),
            VacationRequest("5", "6", "Davi", "2026-11-08", "2026-11-10", "Rejeitada"),
            VacationRequest("6", "7", "Eva", "2026-11-08", "2026-11-10", "Aprovada"),
        ]

        self.assertEqual(
            vacation_service.count_current_vacation_employees(
                requests, today=date(2026, 11, 8)
            ),
            2,
        )


if __name__ == "__main__":
    unittest.main()
