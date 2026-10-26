import inspect
import unittest
from unittest.mock import AsyncMock, patch

from Gestao_RH_Impacta import Gestao_RH_Impacta as app_module
from Gestao_RH_Impacta import employee_service
from Gestao_RH_Impacta.auth_service import AuthenticatedUser, SessionRejected
from Gestao_RH_Impacta.employee_service import (
    Employee,
    EmployeeCreationError,
    EmployeeDepartmentOption,
    EmployeeFormOptions,
    EmployeeUserOption,
)


async def run_loader(state):
    events = []
    async for event in state.load_employees():
        events.append(event)
    return events


async def run_form_opener(state):
    events = []
    async for event in state.open_employee_form():
        events.append(event)
    return events


async def run_submit(state):
    events = []
    async for event in state.submit_employee():
        events.append(event)
    return events


class EmployeeListStateTests(unittest.IsolatedAsyncioTestCase):
    def make_state(self):
        state = app_module.State(_reflex_internal_init=True)
        state._auth_token = "fixture-token"
        state._authenticated = True
        return state

    async def test_loads_and_exposes_only_directory_fields(self):
        state = self.make_state()
        employee = employee_service.Employee(
            id="3",
            name="Joana Silva",
            department="Produto",
            job_title="Analista",
            admission_date="2024-03-01",
            status="Ativo",
        )
        with (
            patch.object(
                app_module, "get_authenticated_user"
            ) as get_user,
            patch.object(
                app_module, "list_employees", return_value=[employee]
            ),
        ):
            await run_loader(state)

        self.assertTrue(state.is_authenticated)
        self.assertEqual(state.employee_list_status, "loaded")
        self.assertEqual(state.employee_rows[0]["name"], "Joana Silva")
        self.assertEqual(state.employee_rows[0]["department"], "Produto")
        self.assertNotIn("salario", state.employee_rows[0])
        self.assertNotIn("fixture-token", str(state.get_delta()))
        get_user.assert_not_called()

    async def test_empty_response_uses_empty_state(self):
        state = self.make_state()
        with (
            patch.object(
                app_module,
                "get_authenticated_user",
                return_value=AuthenticatedUser(
                    token="fixture-token", user_name="Gestora"
                ),
            ),
            patch.object(app_module, "list_employees", return_value=[]),
        ):
            await run_loader(state)

        self.assertEqual(state.employee_list_status, "empty")
        self.assertEqual(state.employee_rows, [])
        self.assertEqual(state.employee_active_count, "0")

    async def test_active_count_uses_only_active_employees(self):
        state = self.make_state()
        employees = [
            Employee("1", "Ana", "RH", "Analista", "2024-01-10", "Ativo"),
            Employee("2", "Bia", "RH", "Analista", "2024-01-10", "Inativo"),
            Employee("3", "Caio", "RH", "Analista", "2024-01-10", "Ativo"),
        ]
        with patch.object(app_module, "list_employees", return_value=employees):
            await run_loader(state)

        self.assertEqual(state.employee_active_count, "2")

    async def test_loading_state_is_yielded_before_api_response(self):
        state = self.make_state()
        employee = employee_service.Employee(
            id="4",
            name="Ana Costa",
            department="RH",
            job_title="Analista",
            admission_date="2024-01-10",
            status="Ativo",
        )
        with (
            patch.object(
                app_module,
                "get_authenticated_user",
                return_value=AuthenticatedUser(
                    token="fixture-token", user_name="Gestora"
                ),
            ),
            patch.object(app_module, "list_employees", return_value=[employee]),
        ):
            loader = state.load_employees()
            await loader.__anext__()
            self.assertEqual(state.employee_list_status, "loading")
            self.assertEqual(state.employee_active_count, "")
            await loader.__anext__()
            self.assertEqual(state.employee_list_status, "loaded")
            with self.assertRaises(StopAsyncIteration):
                await loader.__anext__()

    async def test_refresh_keeps_cached_rows_visible_until_response(self):
        state = self.make_state()
        cached_row = {
            "id": "3",
            "name": "Joana Silva",
            "department": "Produto",
            "job_title": "Analista",
            "admission_date": "2024-03-01",
            "status": "Ativo",
        }
        employee = Employee(
            id="4",
            name="Ana Costa",
            department="RH",
            job_title="Analista",
            admission_date="2024-01-10",
            status="Ativo",
        )
        state.employee_rows = [cached_row]
        state.employee_active_count = "1"
        state.employee_list_status = "loaded"
        with patch.object(app_module, "list_employees", return_value=[employee]):
            loader = state.load_employees()
            await loader.__anext__()
            self.assertEqual(state.employee_list_status, "loading")
            self.assertEqual(state.employee_rows, [cached_row])
            await loader.__anext__()

        self.assertEqual(state.employee_rows[0]["id"], "4")
        self.assertEqual(state.employee_list_status, "loaded")

    async def test_failed_refresh_keeps_cached_rows_and_reports_error(self):
        state = self.make_state()
        cached_row = {
            "id": "3",
            "name": "Joana Silva",
            "department": "Produto",
            "job_title": "Analista",
            "admission_date": "2024-03-01",
            "status": "Ativo",
        }
        state.employee_rows = [cached_row]
        state.employee_list_status = "loaded"
        with patch.object(
            app_module,
            "list_employees",
            side_effect=employee_service.EmployeeDirectoryError(
                "Consulta indisponível."
            ),
        ):
            await run_loader(state)

        self.assertEqual(state.employee_rows, [cached_row])
        self.assertEqual(state.employee_list_status, "error")
        self.assertEqual(state.employee_list_error, "Consulta indisponível.")
        self.assertEqual(state.employee_active_count, "")

    async def test_access_denial_remains_an_error(self):
        state = self.make_state()
        with (
            patch.object(
                app_module,
                "get_authenticated_user",
                return_value=AuthenticatedUser(
                    token="fixture-token", user_name="Usuário"
                ),
            ),
            patch.object(
                app_module,
                "list_employees",
                side_effect=employee_service.EmployeeAccessDenied(
                    "Sem autorização."
                ),
            ),
            patch.object(
                app_module,
                "get_authenticated_user",
                return_value=AuthenticatedUser(
                    token="fixture-token", user_name="Usuário"
                ),
            ),
        ):
            await run_loader(state)

        self.assertEqual(state.employee_list_status, "error")
        self.assertEqual(state.employee_rows, [])
        self.assertEqual(state.employee_list_error, "Sem autorização.")
        self.assertTrue(state.is_authenticated)

    async def test_expired_session_clears_session_and_redirects(self):
        state = self.make_state()
        with (
            patch.object(
                app_module,
                "get_authenticated_user",
                side_effect=SessionRejected("Sessão expirada."),
            ),
            patch.object(
                app_module,
                "list_employees",
                side_effect=employee_service.EmployeeAccessDenied(
                    "Sem autorização."
                ),
            ),
        ):
            events = await run_loader(state)

        self.assertEqual(state.employee_list_status, "error")
        self.assertFalse(state.is_authenticated)
        self.assertEqual(state._auth_token, "")
        self.assertTrue(events)

    async def test_page_uses_dynamic_rows_and_has_no_fixed_people(self):
        source = inspect.getsource(app_module.colaboradores)

        self.assertIn("State.employee_rows", source)
        self.assertIn("State.employee_list_status", source)
        self.assertIn("State.employee_active_count", source)
        self.assertIn("COLABORADORES ATIVOS", source)
        self.assertIn("EM FÉRIAS", source)
        self.assertNotIn("PENDÊNCIAS", source)
        self.assertNotIn("Marina Nunes", source)
        self.assertNotIn("Rafael Costa", source)
        self.assertNotIn("Camila Souza", source)
        self.assertNotIn("André Lima", source)


class EmployeeFormStateTests(unittest.IsolatedAsyncioTestCase):
    def make_state(self):
        state = app_module.State(_reflex_internal_init=True)
        state._auth_token = "fixture-token"
        state._authenticated = True
        return state

    def set_valid_form(self, state):
        state.employee_form_status = "ready"
        state.employee_department_options = [{"id": "8", "label": "Produto"}]
        state.employee_user_options = [
            {"id": "3", "label": "Joana Silva (conta #3)"}
        ]
        state.employee_form_name = "Joana Silva"
        state.employee_form_user_id = "3"
        state.employee_form_department_id = "8"
        state.employee_form_job_title = "Analista"
        state.employee_form_admission_date = "2024-03-01"

    async def test_open_form_loads_only_options_from_service(self):
        state = self.make_state()
        options = EmployeeFormOptions(
            departments=[EmployeeDepartmentOption("8", "Produto")],
            users=[EmployeeUserOption("3", "Joana Silva")],
        )
        with patch.object(
            app_module, "get_employee_form_options", return_value=options
        ):
            await run_form_opener(state)

        self.assertEqual(state.employee_form_status, "ready")
        self.assertTrue(state.employee_form_open)
        self.assertEqual(
            state.employee_department_options,
            [{"id": "8", "label": "Produto"}],
        )
        self.assertEqual(
            state.employee_user_options,
            [{"id": "3", "label": "Joana Silva (conta #3)"}],
        )

    async def test_options_failure_is_visible_without_fake_choices(self):
        state = self.make_state()
        with patch.object(
            app_module,
            "get_employee_form_options",
            side_effect=EmployeeCreationError("Consulta indisponível."),
        ):
            await run_form_opener(state)

        self.assertEqual(state.employee_form_status, "error")
        self.assertEqual(state.employee_form_error, "Consulta indisponível.")
        self.assertEqual(state.employee_department_options, [])
        self.assertEqual(state.employee_user_options, [])

    async def test_required_selections_and_date_are_validated(self):
        state = self.make_state()
        self.set_valid_form(state)
        state.employee_form_name = " "
        with patch.object(app_module, "create_employee", new_callable=AsyncMock) as create:
            await run_submit(state)

        self.assertEqual(state.employee_form_error, "Informe o nome do funcionário.")
        create.assert_not_awaited()

        state.employee_form_name = "Joana Silva"
        state.employee_form_user_id = ""
        with patch.object(app_module, "create_employee", new_callable=AsyncMock) as create:
            await run_submit(state)

        self.assertEqual(state.employee_form_error, "Selecione uma conta existente.")
        create.assert_not_awaited()

        state.employee_form_user_id = "3"
        state.employee_form_department_id = ""
        with patch.object(app_module, "create_employee", new_callable=AsyncMock) as create:
            await run_submit(state)

        self.assertEqual(state.employee_form_error, "Selecione um departamento.")
        self.assertEqual(state.employee_form_name, "Joana Silva")
        create.assert_not_awaited()

        state.employee_form_department_id = "8"
        state.employee_form_admission_date = "data-inválida"
        with patch.object(app_module, "create_employee", new_callable=AsyncMock) as create:
            await run_submit(state)

        self.assertEqual(
            state.employee_form_error,
            "Informe uma data de admissão válida.",
        )
        self.assertEqual(state.employee_form_name, "Joana Silva")
        self.assertEqual(state.employee_form_job_title, "Analista")
        create.assert_not_awaited()

    async def test_create_error_preserves_values_and_allows_retry(self):
        state = self.make_state()
        self.set_valid_form(state)
        create = AsyncMock(
            side_effect=[
                EmployeeCreationError("Falha ao cadastrar."),
                "22",
            ]
        )
        employees = [
            Employee(
                id="22",
                name="Nome persistido no Xano",
                department="Produto",
                job_title="Analista",
                admission_date="2024-03-01",
                status="Ativo",
            )
        ]
        with (
            patch.object(app_module, "create_employee", create),
            patch.object(
                app_module,
                "list_employees",
                new_callable=AsyncMock,
                return_value=employees,
            ) as list_employees,
        ):
            await run_submit(state)
            self.assertEqual(state.employee_form_status, "error")
            self.assertEqual(state.employee_form_error, "Falha ao cadastrar.")
            self.assertEqual(state.employee_form_name, "Joana Silva")
            self.assertEqual(state.employee_form_department_id, "8")
            self.assertEqual(state.employee_form_job_title, "Analista")
            self.assertEqual(state.employee_form_admission_date, "2024-03-01")

            await run_submit(state)

        self.assertEqual(create.await_count, 2)
        list_employees.assert_awaited_once()
        self.assertEqual(
            state.employee_form_success,
            "Funcionário cadastrado e confirmado na listagem.",
        )
        self.assertFalse(state.employee_form_open)
        self.assertEqual(state.employee_list_status, "loaded")
        self.assertEqual(
            state.employee_rows[0]["name"], "Nome persistido no Xano"
        )
        self.assertEqual(state.employee_rows[0]["department"], "Produto")
        self.assertEqual(state.employee_rows[0]["admission_date"], "2024-03-01")
        self.assertEqual(state.employee_rows[0]["status"], "Ativo")
        self.assertEqual(state.employee_active_count, "1")
        self.assertNotIn("salario", state.employee_rows[0])

    async def test_successful_post_missing_from_get_is_not_counted_as_persisted(self):
        state = self.make_state()
        self.set_valid_form(state)
        with (
            patch.object(
                app_module, "create_employee", new_callable=AsyncMock,
                return_value="22",
            ),
            patch.object(
                app_module, "list_employees", new_callable=AsyncMock,
                return_value=[],
            ) as list_employees,
        ):
            await run_submit(state)

        list_employees.assert_awaited_once()
        self.assertEqual(state.employee_rows, [])
        self.assertEqual(state.employee_active_count, "0")
        self.assertEqual(state.employee_list_status, "error")
        self.assertIn("GET /employees", state.employee_form_success)
        self.assertIn("não cadastre novamente", state.employee_form_success)

    def test_form_is_connected_and_does_not_request_salary(self):
        source = inspect.getsource(app_module.colaboradores)

        self.assertIn("State.open_employee_form", source)
        self.assertIn("State.submit_employee", source)
        self.assertIn("State.employee_form_error", source)
        self.assertIn("State.employee_form_name", source)
        self.assertIn("Nome completo", source)
        self.assertIn("Conta existente", source)
        self.assertNotIn("salário", source.lower())
        self.assertNotIn("salary", source.lower())


if __name__ == "__main__":
    unittest.main()
