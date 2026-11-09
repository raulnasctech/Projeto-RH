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


if __name__ == "__main__":
    unittest.main()
