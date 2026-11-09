import inspect
import unittest
from unittest.mock import patch

from Gestao_RH_Impacta import Gestao_RH_Impacta as app_module
from Gestao_RH_Impacta.work_schedule_service import (
    WorkSchedule,
    WorkScheduleError,
    empty_work_week,
)


async def run_generator(generator):
    events = []
    async for event in generator:
        events.append(event)
    return events


def saved_work_schedule(schedule_id="15"):
    days = empty_work_week()
    days[0].update(
        is_workday="true",
        start_time="08:00",
        end_time="17:00",
        break_start_time="12:00",
        break_end_time="13:00",
    )
    return WorkSchedule(id=schedule_id, employee_id="3", days=days)


class WorkScheduleStateTests(unittest.IsolatedAsyncioTestCase):
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

    async def test_missing_schedule_loads_empty_form(self):
        state = self.make_state()
        with patch.object(
            app_module, "get_work_schedule", return_value=None
        ) as get_schedule:
            await run_generator(state.select_work_schedule_employee("3"))

        get_schedule.assert_awaited_once()
        self.assertEqual(state.work_schedule_load_status, "empty")
        self.assertEqual(len(state.work_schedule_days), 7)
        self.assertEqual(state.work_schedule_saved_days, [])
        self.assertEqual(state.work_schedule_id, "")

    async def test_loads_confirmed_schedule_and_saved_snapshot(self):
        state = self.make_state()
        schedule = saved_work_schedule()
        with patch.object(
            app_module, "get_work_schedule", return_value=schedule
        ):
            await run_generator(state.select_work_schedule_employee("3"))

        self.assertEqual(state.work_schedule_load_status, "loaded")
        self.assertEqual(state.work_schedule_id, "15")
        self.assertEqual(state.work_schedule_days[0]["start_time"], "08:00")
        self.assertEqual(state.work_schedule_saved_days[0]["end_time"], "17:00")

    async def test_failed_load_is_explicit_and_does_not_create_empty_schedule(self):
        state = self.make_state()
        with patch.object(
            app_module,
            "get_work_schedule",
            side_effect=WorkScheduleError("Consulta recusada."),
        ):
            await run_generator(state.select_work_schedule_employee("3"))

        self.assertEqual(state.work_schedule_load_status, "error")
        self.assertEqual(state.work_schedule_load_error, "Consulta recusada.")
        self.assertEqual(state.work_schedule_days, [])

    async def test_save_uses_confirmed_response_as_new_saved_snapshot(self):
        state = self.make_state()
        state.work_schedule_employee_id = "3"
        state.work_schedule_load_status = "empty"
        state.work_schedule_days = saved_work_schedule().days
        confirmed = saved_work_schedule(schedule_id="22")
        with patch.object(
            app_module, "save_work_schedule", return_value=confirmed
        ) as save_schedule:
            await run_generator(state.submit_work_schedule())

        save_schedule.assert_awaited_once()
        self.assertEqual(state.work_schedule_load_status, "loaded")
        self.assertEqual(state.work_schedule_save_status, "saved")
        self.assertEqual(state.work_schedule_id, "22")
        self.assertEqual(state.work_schedule_save_success, "Jornada semanal salva e confirmada pelo Xano.")
        self.assertEqual(state.work_schedule_saved_days[0]["start_time"], "08:00")

    async def test_failed_save_preserves_previous_confirmed_schedule(self):
        state = self.make_state()
        confirmed = saved_work_schedule()
        state.work_schedule_employee_id = "3"
        state.work_schedule_id = confirmed.id
        state.work_schedule_load_status = "loaded"
        state.work_schedule_days = [dict(day) for day in confirmed.days]
        state.work_schedule_saved_days = [dict(day) for day in confirmed.days]
        state.set_work_schedule_day_field("monday", "end_time", "18:00")

        with patch.object(
            app_module,
            "save_work_schedule",
            side_effect=WorkScheduleError("Salvamento recusado."),
        ):
            await run_generator(state.submit_work_schedule())

        self.assertEqual(state.work_schedule_save_status, "error")
        self.assertEqual(state.work_schedule_save_error, "Salvamento recusado.")
        self.assertEqual(state.work_schedule_days[0]["end_time"], "18:00")
        self.assertEqual(state.work_schedule_saved_days[0]["end_time"], "17:00")

    async def test_turning_a_workday_into_a_rest_day_clears_times(self):
        state = self.make_state()
        state.work_schedule_days = saved_work_schedule().days
        state.set_work_schedule_day_workday("monday", False)

        self.assertEqual(state.work_schedule_days[0]["is_workday"], "false")
        self.assertEqual(state.work_schedule_days[0]["start_time"], "")
        self.assertEqual(state.work_schedule_days[0]["end_time"], "")
        self.assertEqual(state.work_schedule_days[0]["break_start_time"], "")

    async def test_rejects_nonexistent_employee_without_request(self):
        state = self.make_state()
        await run_generator(state.select_work_schedule_employee("99"))

        self.assertEqual(state.work_schedule_load_status, "error")
        self.assertEqual(state.work_schedule_load_error, "Selecione um colaborador existente.")

    def test_schedule_page_exposes_selector_states_and_week_editor(self):
        source = inspect.getsource(app_module.jornadas)
        self.assertIn("State.select_work_schedule_employee", source)
        self.assertIn("State.work_schedule_load_status", source)
        self.assertIn("State.set_work_schedule_day_workday", source)
        self.assertIn("State.set_work_schedule_day_field", source)
        self.assertIn("State.submit_work_schedule", source)
        self.assertIn("type=\"time\"", source)
        self.assertIn("Restaurar última versão salva", source)
        app_source = inspect.getsource(app_module)
        self.assertIn("jornadas", app_source)

    def test_schedule_page_authenticates_before_loading_employees(self):
        source = inspect.getsource(
            app_module.State.load_work_schedule_page.fn
        )
        self.assertLess(source.index("require_auth"), source.index("load_employees"))


if __name__ == "__main__":
    unittest.main()
