import inspect
import unittest
from datetime import date, timedelta
from unittest.mock import patch

from Gestao_RH_Impacta import Gestao_RH_Impacta as app_module
from Gestao_RH_Impacta.vacation_service import (
    VacationRequest,
    VacationRequestError,
)


async def run_generator(generator):
    events = []
    async for event in generator:
        events.append(event)
    return events


class VacationStateTests(unittest.IsolatedAsyncioTestCase):
    def make_state(self):
        state = app_module.State(_reflex_internal_init=True)
        state._auth_token = "fixture-token"
        state._authenticated = True
        state.employee_rows = [
            {
                "id": "3",
                "name": "Ana Souza",
                "department": "RH",
                "job_title": "Analista",
                "admission_date": "2024-01-01",
                "status": "Ativo",
            }
        ]
        return state

    async def test_loads_list_and_counts_current_approved_employees(self):
        state = self.make_state()
        today = date.today()
        requests = [
            VacationRequest(
                "1",
                "3",
                "Ana Souza",
                (today - timedelta(days=1)).isoformat(),
                (today + timedelta(days=1)).isoformat(),
                "Aprovada",
            ),
            VacationRequest(
                "2",
                "3",
                "Ana Souza",
                today.isoformat(),
                (today + timedelta(days=2)).isoformat(),
                "Aprovada",
            ),
        ]
        with patch.object(
            app_module, "list_vacation_requests", return_value=requests
        ):
            await run_generator(state.load_vacation_requests())

        self.assertEqual(state.vacation_list_status, "loaded")
        self.assertEqual(state.vacation_count_status, "loaded")
        self.assertEqual(state.employee_vacation_count, "1")
        self.assertEqual(len(state.vacation_rows), 2)

    async def test_empty_and_failed_lists_have_distinct_states(self):
        state = self.make_state()
        with patch.object(
            app_module, "list_vacation_requests", return_value=[]
        ):
            await run_generator(state.load_vacation_requests())
        self.assertEqual(state.vacation_list_status, "empty")
        self.assertEqual(state.employee_vacation_count, "0")

        with patch.object(
            app_module,
            "list_vacation_requests",
            side_effect=VacationRequestError("Falha controlada."),
        ):
            await run_generator(state.load_vacation_requests())
        self.assertEqual(state.vacation_list_status, "error")
        self.assertEqual(state.vacation_count_status, "error")
        self.assertEqual(state.employee_vacation_count, "Indisponível")
        self.assertEqual(state.vacation_list_error, "Falha controlada.")

    async def test_employee_loads_own_history_with_empty_and_error_states(self):
        state = self.make_state()
        state._auth_user_role = "Funcionário"
        request = VacationRequest(
            "19",
            "3",
            "Ana Souza",
            "2026-12-01",
            "2026-12-10",
            "Pendente",
        )
        with patch.object(
            app_module,
            "list_my_vacation_requests",
            return_value=[request],
        ):
            await run_generator(state.load_my_vacation_requests())

        self.assertEqual(state.my_vacation_list_status, "loaded")
        self.assertEqual(state.my_vacation_rows[0]["status"], "Pendente")
        self.assertEqual(state.my_vacation_rows[0]["id"], "19")

        with patch.object(
            app_module, "list_my_vacation_requests", return_value=[]
        ):
            await run_generator(state.load_my_vacation_requests())
        self.assertEqual(state.my_vacation_list_status, "empty")

        with patch.object(
            app_module,
            "list_my_vacation_requests",
            side_effect=VacationRequestError("Falha controlada."),
        ):
            await run_generator(state.load_my_vacation_requests())
        self.assertEqual(state.my_vacation_list_status, "error")
        self.assertEqual(
            state.my_vacation_list_error, "Falha controlada."
        )

    async def test_employee_submission_validates_dates_before_request(self):
        state = self.make_state()
        state._auth_user_role = "Funcionário"
        state.my_vacation_start_date = "2026-12-10"
        state.my_vacation_end_date = "2026-12-01"
        with patch.object(
            app_module, "create_my_vacation_request"
        ) as create_request:
            await run_generator(state.submit_my_vacation_request())

        self.assertIn("não pode ser posterior", state.my_vacation_form_error)
        create_request.assert_not_awaited()

    async def test_employee_submission_adds_confirmed_pending_request(self):
        state = self.make_state()
        state._auth_user_role = "Funcionário"
        state.my_vacation_start_date = "2026-12-01"
        state.my_vacation_end_date = "2026-12-10"
        with (
            patch.object(
                app_module, "create_my_vacation_request", return_value="20"
            ) as create_request,
            patch.object(
                app_module,
                "list_my_vacation_requests",
                return_value=[
                    VacationRequest(
                        "20",
                        "3",
                        "Ana Souza",
                        "2026-12-01",
                        "2026-12-10",
                        "Pendente",
                    )
                ],
            ) as list_requests,
        ):
            await run_generator(state.submit_my_vacation_request())

        create_request.assert_awaited_once_with(
            app_module.XANO_RH_API_URL,
            "fixture-token",
            "2026-12-01",
            "2026-12-10",
        )
        self.assertEqual(state.my_vacation_form_status, "success")
        list_requests.assert_awaited_once()
        self.assertEqual(state.my_vacation_rows[0]["id"], "20")
        self.assertEqual(state.my_vacation_rows[0]["status"], "Pendente")
        self.assertEqual(state.my_vacation_list_status, "loaded")

    async def test_submit_validates_date_order_before_request(self):
        state = self.make_state()
        state.vacation_list_status = "empty"
        state.vacation_form_employee_id = "3"
        state.vacation_form_start_date = "2026-12-10"
        state.vacation_form_end_date = "2026-12-01"
        with patch.object(
            app_module, "create_vacation_request"
        ) as create_request:
            await run_generator(state.submit_vacation_request())

        self.assertIn("não pode ser posterior", state.vacation_form_error)
        create_request.assert_not_awaited()

    async def test_successful_submission_inserts_confirmed_pending_row(self):
        state = self.make_state()
        state.vacation_list_status = "empty"
        state.vacation_form_employee_id = "3"
        state.vacation_form_start_date = "2026-12-01"
        state.vacation_form_end_date = "2026-12-10"
        with patch.object(
            app_module, "create_vacation_request", return_value="15"
        ) as create_request:
            await run_generator(state.submit_vacation_request())

        create_request.assert_awaited_once()
        self.assertEqual(state.vacation_form_status, "success")
        self.assertEqual(state.vacation_rows[0]["id"], "15")
        self.assertEqual(state.vacation_rows[0]["employee_name"], "Ana Souza")
        self.assertEqual(state.vacation_rows[0]["status"], "Pendente")
        self.assertEqual(state.vacation_list_status, "loaded")

    async def test_decision_updates_row_and_metric_after_backend_confirmation(self):
        state = self.make_state()
        today = date.today()
        state.vacation_rows = [
            {
                "id": "1",
                "employee_id": "3",
                "employee_name": "Ana Souza",
                "start_date": today.isoformat(),
                "end_date": (today + timedelta(days=3)).isoformat(),
                "status": "Pendente",
            }
        ]
        with patch.object(
            app_module, "decide_vacation_request"
        ) as decide_request:
            await run_generator(
                state.decide_vacation_request("1", "Aprovada")
            )

        decide_request.assert_awaited_once()
        self.assertEqual(state.vacation_rows[0]["status"], "Aprovada")
        self.assertEqual(state.employee_vacation_count, "1")

    async def test_failed_decision_does_not_change_list(self):
        state = self.make_state()
        state.vacation_rows = [
            {
                "id": "1",
                "employee_id": "3",
                "employee_name": "Ana Souza",
                "start_date": "2026-12-01",
                "end_date": "2026-12-10",
                "status": "Pendente",
            }
        ]
        with patch.object(
            app_module,
            "decide_vacation_request",
            side_effect=VacationRequestError("Decisão recusada."),
        ):
            await run_generator(
                state.decide_vacation_request("1", "Aprovada")
            )

        self.assertEqual(state.vacation_rows[0]["status"], "Pendente")
        self.assertEqual(state.vacation_action_error, "Decisão recusada.")

    def test_vacation_page_is_registered_with_management_actions(self):
        source = inspect.getsource(app_module.ferias)
        self.assertIn("State.submit_vacation_request", source)
        self.assertIn("State.decide_vacation_request", source)
        self.assertIn("State.vacation_list_status", source)
        self.assertIn("Aprovar", source)
        self.assertIn("Rejeitar", source)
        self.assertNotIn("Excluir", source)

    def test_vacation_page_and_employee_navigation_support_both_profiles(self):
        page_source = inspect.getsource(app_module.ferias)
        sidebar_source = inspect.getsource(app_module.app_sidebar)
        loader_source = inspect.getsource(app_module.State)
        module_source = inspect.getsource(app_module)
        self.assertIn("State.submit_my_vacation_request", page_source)
        self.assertIn("State.my_vacation_rows", page_source)
        self.assertIn("State.user_role == \"Gestor RH\"", page_source)
        self.assertIn('navigation_item("Minhas férias", "/ferias"', sidebar_source)
        self.assertIn('self._auth_user_role == "Gestor RH"', loader_source)
        self.assertIn("on_load=State.load_vacation_page", module_source)

    def test_sidebar_removes_profile_link_and_rh_help_cards(self):
        dashboard_source = inspect.getsource(app_module.dashboard)
        sidebar_source = inspect.getsource(app_module.app_sidebar)

        for source in (dashboard_source, sidebar_source):
            with self.subTest(sidebar="dashboard" if source == dashboard_source else "shared"):
                self.assertNotIn('navigation_item("Perfil", "/perfil")', source)
                self.assertNotIn('("Perfil", "/perfil", "perfil")', source)
                self.assertNotIn("PRECISA DE AJUDA?", source)
                self.assertNotIn("Suporte RH", source)
                self.assertNotIn("Fale com o RH", source)

    def test_profile_route_remains_registered(self):
        pages = app_module.app._unevaluated_pages

        self.assertIn("perfil", pages)
        self.assertIn('route="/perfil"', inspect.getsource(app_module))


if __name__ == "__main__":
    unittest.main()
