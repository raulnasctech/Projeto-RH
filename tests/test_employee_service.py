import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

from Gestao_RH_Impacta import employee_service
ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = ROOT / "xano" / "api" / "rh_api" / "employees_GET.xs"


class FakeAsyncClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False

    async def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if isinstance(self.response, Exception):
            raise self.response
        return self.response

    async def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if isinstance(self.response, Exception):
            raise self.response
        return self.response

    async def patch(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


class EmployeeServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_lists_employees_with_auth_and_only_display_fields(self):
        client = FakeAsyncClient(
            httpx.Response(
                200,
                json=[
                    {
                        "id": 9,
                        "employee_name": "Joana Silva",
                        "department": "Produto",
                        "job_title": "Analista",
                        "admissao": "2024-03-01",
                        "status": "Ativo",
                    }
                ],
            )
        )
        with patch.object(
            employee_service.httpx, "AsyncClient", return_value=client
        ):
            employees = await employee_service.list_employees(
                "https://example.xano.io/api:rh", "fixture-token"
            )

        self.assertEqual(employees[0].name, "Joana Silva")
        self.assertEqual(employees[0].department, "Produto")
        self.assertEqual(
            employees[0].as_dict(),
            {
                "id": "9",
                "name": "Joana Silva",
                "department": "Produto",
                "job_title": "Analista",
                "admission_date": "2024-03-01",
                "status": "Ativo",
            },
        )
        self.assertNotIn("salario", employees[0].as_dict())
        self.assertEqual(
            client.calls[0][0],
            "https://example.xano.io/api:rh/employees",
        )
        self.assertEqual(
            client.calls[0][1]["headers"]["Authorization"],
            "Bearer fixture-token",
        )

    async def test_missing_optional_values_are_explicit(self):
        client = FakeAsyncClient(httpx.Response(200, json=[{"id": 9}]))
        with patch.object(
            employee_service.httpx, "AsyncClient", return_value=client
        ):
            employees = await employee_service.list_employees(
                "https://example.xano.io/api:rh", "fixture-token"
            )

        self.assertEqual(employees[0].name, "Não informado")
        self.assertEqual(employees[0].department, "Não informado")
        self.assertEqual(employees[0].job_title, "Não informado")
        self.assertEqual(employees[0].admission_date, "Não informado")
        self.assertEqual(employees[0].status, "Não informado")

    async def test_prefers_employee_name_over_related_account_name(self):
        client = FakeAsyncClient(
            httpx.Response(
                200,
                json=[
                    {
                        "id": 9,
                        "employee_name": "Nome informado no cadastro",
                        "name": "Nome da conta",
                    }
                ],
            )
        )
        with patch.object(
            employee_service.httpx, "AsyncClient", return_value=client
        ):
            employees = await employee_service.list_employees(
                "https://example.xano.io/api:rh", "fixture-token"
            )

        self.assertEqual(employees[0].name, "Nome informado no cadastro")

    async def test_empty_list_is_a_successful_empty_result(self):
        client = FakeAsyncClient(httpx.Response(200, json=[]))
        with patch.object(
            employee_service.httpx, "AsyncClient", return_value=client
        ):
            employees = await employee_service.list_employees(
                "https://example.xano.io/api:rh", "fixture-token"
            )

        self.assertEqual(employees, [])

    async def test_unauthorized_response_is_reported_as_access_denial(self):
        client = FakeAsyncClient(httpx.Response(401, json={"message": "Unauthorized"}))
        with patch.object(
            employee_service.httpx, "AsyncClient", return_value=client
        ):
            with self.assertRaises(employee_service.EmployeeAccessDenied):
                await employee_service.list_employees(
                    "https://example.xano.io/api:rh", "fixture-token"
                )

    async def test_forbidden_response_is_access_denied(self):
        client = FakeAsyncClient(httpx.Response(403, json={"message": "Forbidden"}))
        with patch.object(
            employee_service.httpx, "AsyncClient", return_value=client
        ):
            with self.assertRaises(employee_service.EmployeeAccessDenied):
                await employee_service.list_employees(
                    "https://example.xano.io/api:rh", "fixture-token"
                )

    async def test_server_error_is_not_converted_to_empty_list(self):
        client = FakeAsyncClient(httpx.Response(500, json={"message": "Failure"}))
        with patch.object(
            employee_service.httpx, "AsyncClient", return_value=client
        ):
            with self.assertRaises(employee_service.EmployeeDirectoryError):
                await employee_service.list_employees(
                    "https://example.xano.io/api:rh", "fixture-token"
                )

    async def test_connection_failure_is_not_converted_to_empty_list(self):
        client = FakeAsyncClient(httpx.ConnectError("connection failed"))
        with patch.object(
            employee_service.httpx, "AsyncClient", return_value=client
        ):
            with self.assertRaises(httpx.ConnectError):
                await employee_service.list_employees(
                    "https://example.xano.io/api:rh", "fixture-token"
                )

    async def test_unexpected_response_shapes_are_rejected(self):
        for payload in ({"items": []}, [None], [{"id": 2, "name": 17}], [{}]):
            client = FakeAsyncClient(httpx.Response(200, json=payload))
            with (
                self.subTest(payload=payload),
                patch.object(
                    employee_service.httpx, "AsyncClient", return_value=client
                ),
                self.assertRaises(employee_service.EmployeeDirectoryError),
            ):
                await employee_service.list_employees(
                    "https://example.xano.io/api:rh", "fixture-token"
                )

    async def test_loads_employee_form_options_with_minimal_fields(self):
        client = FakeAsyncClient(
            httpx.Response(
                200,
                json={
                    "departments": [{"id": 8, "nome": "Produto"}],
                    "users": [{"id": 3, "name": "Joana Silva"}],
                },
            )
        )
        with patch.object(
            employee_service.httpx, "AsyncClient", return_value=client
        ):
            options = await employee_service.get_employee_form_options(
                "https://example.xano.io/api:rh/", "fixture-token"
            )

        self.assertEqual(options.departments[0].as_dict(), {
            "id": "8",
            "label": "Produto",
        })
        self.assertEqual(
            options.users[0].as_dict(),
            {"id": "3", "label": "Joana Silva (conta #3)"},
        )
        self.assertEqual(
            client.calls[0][0],
            "https://example.xano.io/api:rh/employee-form-options",
        )
        self.assertEqual(
            client.calls[0][1]["headers"]["Authorization"],
            "Bearer fixture-token",
        )

    async def test_ignores_extra_account_fields_and_uses_only_id_and_name(self):
        client = FakeAsyncClient(
            httpx.Response(
                200,
                json={
                    "users": [
                        {"id": 3, "name": "Conta", "email": "c@example.com"}
                    ],
                    "departments": [{"id": 8, "nome": "Produto"}],
                },
            )
        )
        with patch.object(
            employee_service.httpx, "AsyncClient", return_value=client
        ):
            options = await employee_service.get_employee_form_options(
                "https://example.xano.io/api:rh", "fixture-token"
            )

        self.assertEqual(
            [option.as_dict() for option in options.users],
            [{"id": "3", "label": "Conta (conta #3)"}],
        )
        self.assertFalse(hasattr(options.users[0], "email"))

    async def test_rejects_user_record_without_name(self):
        client = FakeAsyncClient(
            httpx.Response(
                200,
                json={
                    "users": [{"id": 3, "email": "c@example.com"}],
                    "departments": [{"id": 8, "nome": "Produto"}],
                },
            )
        )
        with (
            patch.object(
                employee_service.httpx, "AsyncClient", return_value=client
            ),
            self.assertRaises(employee_service.EmployeeCreationError),
        ):
            await employee_service.get_employee_form_options(
                "https://example.xano.io/api:rh", "fixture-token"
            )

    async def test_rejects_invalid_employee_form_options(self):
        for payload in (
            [],
            {"departments": {}},
            {"items": [], "departments": []},
            {"departments": [{"id": 1}]},
            {"departments": [], "users": [{"id": 1}]},
        ):
            client = FakeAsyncClient(httpx.Response(200, json=payload))
            with (
                self.subTest(payload=payload),
                patch.object(
                    employee_service.httpx, "AsyncClient", return_value=client
                ),
                self.assertRaises(employee_service.EmployeeCreationError),
            ):
                await employee_service.get_employee_form_options(
                    "https://example.xano.io/api:rh", "fixture-token"
                )

    async def test_requires_account_options_from_updated_xano_endpoint(self):
        client = FakeAsyncClient(
            httpx.Response(200, json={"departments": []})
        )
        with (
            patch.object(
                employee_service.httpx, "AsyncClient", return_value=client
            ),
            self.assertRaisesRegex(
                employee_service.EmployeeCreationError,
                "Atualize a rota de opções no Xano",
            ),
        ):
            await employee_service.get_employee_form_options(
                "https://example.xano.io/api:rh", "fixture-token"
            )

    async def test_forbidden_employee_options_are_denied(self):
        client = FakeAsyncClient(httpx.Response(403, json={"message": "Forbidden"}))
        with (
            patch.object(
                employee_service.httpx, "AsyncClient", return_value=client
            ),
            self.assertRaises(employee_service.EmployeeAccessDenied),
        ):
            await employee_service.get_employee_form_options(
                "https://example.xano.io/api:rh", "fixture-token"
            )

    async def test_creates_employee_with_an_existing_access_account(self):
        client = FakeAsyncClient(httpx.Response(200, json={"id": 22}))
        with patch.object(
            employee_service.httpx, "AsyncClient", return_value=client
        ):
            employee_id = await employee_service.create_employee(
                "https://example.xano.io/api:rh",
                "fixture-token",
                " Joana Silva ",
                "3",
                "8",
                " Analista ",
                "2026-10-24",
            )

        self.assertEqual(employee_id, "22")
        self.assertEqual(
            client.calls[0][0],
            "https://example.xano.io/api:rh/employees",
        )
        self.assertEqual(
            client.calls[0][1]["headers"]["Authorization"],
            "Bearer fixture-token",
        )
        self.assertEqual(
            client.calls[0][1]["json"],
            {
                "name": "Joana Silva",
                "user_id": 3,
                "departaments_id": 8,
                "job_title": "Analista",
                "admissao": "2026-10-24",
            },
        )
        self.assertNotIn("salario", client.calls[0][1]["json"])
        self.assertNotIn("password", client.calls[0][1]["json"])

    async def test_creation_omits_optional_fields_and_rejects_bad_ids(self):
        client = FakeAsyncClient(httpx.Response(200, json={"id": 23}))
        with patch.object(
            employee_service.httpx, "AsyncClient", return_value=client
        ):
            await employee_service.create_employee(
                "https://example.xano.io/api:rh",
                "fixture-token",
                "Joana",
                "3",
                "8",
                " ",
                "",
            )

        self.assertEqual(
            client.calls[0][1]["json"],
            {"name": "Joana", "user_id": 3, "departaments_id": 8},
        )
        with self.assertRaises(employee_service.EmployeeCreationError):
            await employee_service.create_employee(
                "https://example.xano.io/api:rh",
                "fixture-token",
                "Joana",
                "not-an-id",
                "8",
                "",
                "",
            )
        with self.assertRaises(employee_service.EmployeeCreationError):
            await employee_service.create_employee(
                "https://example.xano.io/api:rh",
                "fixture-token",
                "Joana",
                "3",
                "not-an-id",
                "",
                "",
            )
        with self.assertRaises(employee_service.EmployeeCreationError):
            await employee_service.create_employee(
                "https://example.xano.io/api:rh",
                "fixture-token",
                "Joana",
                "",
                "8",
                "",
                "",
            )
        with self.assertRaises(employee_service.EmployeeCreationError):
            await employee_service.create_employee(
                "https://example.xano.io/api:rh",
                "fixture-token",
                " ",
                "3",
                "8",
                "",
                "",
            )

    async def test_creation_rejects_forbidden_and_invalid_responses(self):
        for response in (
            httpx.Response(403, json={"message": "Forbidden"}),
            httpx.Response(500, json={"message": "Failure"}),
            httpx.Response(200, json={"user_id": 3}),
        ):
            client = FakeAsyncClient(response)
            with patch.object(
                employee_service.httpx, "AsyncClient", return_value=client
            ):
                error = (
                    employee_service.EmployeeAccessDenied
                    if response.status_code == 403
                    else employee_service.EmployeeCreationError
                )
                with self.assertRaises(error):
                    await employee_service.create_employee(
                        "https://example.xano.io/api:rh",
                        "fixture-token",
                        "Joana",
                        "3",
                        "8",
                        "",
                        "",
                    )

    async def test_creation_connection_failure_is_not_hidden(self):
        client = FakeAsyncClient(httpx.ConnectError("connection failed"))
        with (
            patch.object(
                employee_service.httpx, "AsyncClient", return_value=client
            ),
            self.assertRaises(httpx.ConnectError),
        ):
            await employee_service.create_employee(
                "https://example.xano.io/api:rh",
                "fixture-token",
                "Joana",
                "3",
                "8",
                "",
                "",
            )

    async def test_get_employee_returns_details(self):
        client = FakeAsyncClient(
            httpx.Response(
                200,
                json={
                    "id": 9,
                    "name": "Joana Silva",
                    "department": "Produto",
                    "job_title": "Analista",
                    "admissao": "2024-03-01",
                    "status": "Ativo",
                },
            )
        )
        with patch.object(
            employee_service.httpx, "AsyncClient", return_value=client
        ):
            emp = await employee_service.get_employee(
                "https://example.xano.io/api:rh", "fixture-token", "9"
            )

        self.assertEqual(emp.id, "9")
        self.assertEqual(emp.name, "Joana Silva")
        self.assertEqual(client.calls[0][0], "https://example.xano.io/api:rh/employees/9")

    async def test_update_employee_sends_patch(self):
        client = FakeAsyncClient(httpx.Response(200, json={"id": 9}))
        with patch.object(
            employee_service.httpx, "AsyncClient", return_value=client
        ):
            await employee_service.update_employee(
                "https://example.xano.io/api:rh",
                "fixture-token",
                "9",
                name="Joana Atualizada",
                status="Inativo",
                department_id="8",
            )

        self.assertEqual(client.calls[0][0], "https://example.xano.io/api:rh/employees/9")
        self.assertEqual(
            client.calls[0][1]["json"],
            {"name": "Joana Atualizada", "status": "Inativo", "departaments_id": 8},
        )


class EmployeeEndpointContractTests(unittest.TestCase):
    def test_endpoint_joins_related_names_and_limits_output_fields(self):
        source = ENDPOINT.read_text(encoding="utf-8")

        authorization_call = source.index(
            'function.run "RH API/authorize employee manager"'
        )
        employee_query = source.index("db.query employees")
        self.assertLess(authorization_call, employee_query)
        self.assertIn('auth = "user"', source)
        self.assertIn('table: "user"', source)
        self.assertIn('table: "departaments"', source)
        self.assertIn(
            'employee_name: $db.employees.name ?? $db.employee_user.name ?? "Não informado"',
            source,
        )
        self.assertIn("department: $db.employee_department.nome", source)
        self.assertIn(
            'output = ["id", "employee_name", "department", "job_title", "admissao", "status"]',
            source,
        )
        self.assertNotIn("salario", source)
