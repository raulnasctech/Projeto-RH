import inspect
import unittest
from unittest.mock import patch

from Gestao_RH_Impacta import Gestao_RH_Impacta as app_module
from Gestao_RH_Impacta import attendance_service


WORK_DATE = "2026-11-09"
EMPLOYEE = {
    "id": 7,
    "employee_name": "Ana Souza",
    "job_title": "Analista",
    "department": "Produto",
    "status": "Ativo",
}
SCHEDULE = {
    "is_workday": True,
    "start_minute": 540,
    "end_minute": 1020,
    "break_start_minute": 720,
    "break_end_minute": 780,
}


def attendance_day(punches=None):
    return attendance_service._parse_my_attendance(
        {
            "employee": EMPLOYEE,
            "work_date": WORK_DATE,
            "server_now": "2026-11-09T10:00:00-03:00",
            "schedule": SCHEDULE,
            "punches": punches or [],
        }
    )


async def run_generator(generator):
    events = []
    async for event in generator:
        events.append(event)
    return events


class AttendanceStateTests(unittest.IsolatedAsyncioTestCase):
    def make_state(self, role="Colaborador"):
        state = app_module.State(_reflex_internal_init=True)
        state._auth_token = "fixture-token"
        state._auth_user_role = role
        state._authenticated = True
        state._skip_next_auth_check = True
        return state

    async def test_employee_load_maps_confirmed_schedule_and_next_punch(self):
        state = self.make_state()
        attendance = attendance_day()
        with patch.object(
            app_module, "get_my_attendance", return_value=attendance
        ) as get_attendance:
            await run_generator(state.load_my_attendance())

        get_attendance.assert_awaited_once()
        self.assertEqual(state.my_attendance_status, "loaded")
        self.assertEqual(state.my_attendance_row["state"], "Não iniciou")
        self.assertIn("Entrada 09:00", state.my_attendance_row["schedule_summary"])
        self.assertEqual(state.my_attendance_row["next_punch_label"], "Entrada")
        self.assertTrue(state.my_attendance_can_punch)

    async def test_manager_is_redirected_from_employee_point_screen(self):
        state = self.make_state(role="Gestor RH")
        with patch.object(app_module, "get_my_attendance") as get_attendance:
            events = await run_generator(state.load_my_attendance())

        self.assertEqual(len(events), 1)
        get_attendance.assert_not_awaited()

    async def test_employee_is_redirected_from_manager_dashboard(self):
        state = self.make_state(role="Colaborador")
        with patch.object(
            app_module, "get_daily_attendance"
        ) as get_attendance:
            events = await run_generator(state.load_attendance_dashboard())

        self.assertEqual(len(events), 1)
        get_attendance.assert_not_awaited()

    async def test_employee_load_failure_does_not_create_empty_attendance(self):
        state = self.make_state()
        with patch.object(
            app_module,
            "get_my_attendance",
            side_effect=attendance_service.AttendanceError(
                "Consulta indisponível."
            ),
        ):
            await run_generator(state.load_my_attendance())

        self.assertEqual(state.my_attendance_status, "error")
        self.assertEqual(state.my_attendance_error, "Consulta indisponível.")
        self.assertEqual(state.my_attendance_row["entry_at"], "")

    async def test_punch_refreshes_from_confirmed_server_state(self):
        state = self.make_state()
        initial = attendance_day()
        state._skip_next_auth_check = False
        state.my_attendance_status = "loaded"
        state.my_attendance_can_punch = True
        state.my_attendance_row = initial.as_dict()
        confirmed = attendance_day(
            [
                {
                    "punch_type": "entry",
                    "punched_at": "2026-11-09T09:59:00-03:00",
                }
            ]
        )
        with (
            patch.object(
                app_module, "record_next_punch", return_value=confirmed
            ) as record_punch,
            patch.object(
                app_module, "get_my_attendance", return_value=confirmed
            ) as get_attendance,
        ):
            await run_generator(state.record_attendance_punch())

        record_punch.assert_awaited_once()
        get_attendance.assert_awaited_once()
        self.assertEqual(state.my_attendance_status, "loaded")
        self.assertEqual(state.my_attendance_row["entry_at"], "09:59")
        self.assertIn("Entrada registrada", state.my_attendance_success)

    async def test_punch_is_not_sent_before_expected_time(self):
        state = self.make_state()
        state.my_attendance_status = "loaded"
        state.my_attendance_can_punch = False
        with patch.object(app_module, "record_next_punch") as record_punch:
            await run_generator(state.record_attendance_punch())

        record_punch.assert_not_awaited()
        self.assertEqual(state.my_attendance_status, "loaded")
        self.assertEqual(state.my_attendance_success, "")
        self.assertNotEqual(state.my_attendance_error, "")

    async def test_manager_dashboard_maps_rows_and_counts(self):
        state = self.make_state(role="Gestor RH")
        state._skip_next_auth_check = True
        rows = [attendance_day()]
        with patch.object(
            app_module, "get_daily_attendance", return_value=rows
        ) as get_attendance:
            await run_generator(state.load_attendance_dashboard())

        get_attendance.assert_awaited_once()
        self.assertEqual(state.attendance_dashboard_status, "loaded")
        self.assertEqual(state.attendance_dashboard_rows[0]["employee_name"], "Ana Souza")
        self.assertEqual(state.attendance_state_counts["Não iniciou"], "1")

    async def test_manager_dashboard_failure_is_not_empty_state(self):
        state = self.make_state(role="Gestor RH")
        with patch.object(
            app_module,
            "get_daily_attendance",
            side_effect=attendance_service.AttendanceError(
                "Painel indisponível."
            ),
        ):
            await run_generator(state.load_attendance_dashboard())

        self.assertEqual(state.attendance_dashboard_status, "error")
        self.assertEqual(
            state.attendance_dashboard_error, "Painel indisponível."
        )

    async def test_empty_manager_dashboard_has_an_explicit_empty_state(self):
        state = self.make_state(role="Gestor RH")
        with patch.object(
            app_module, "get_daily_attendance", return_value=[]
        ):
            await run_generator(state.load_attendance_dashboard())

        self.assertEqual(state.attendance_dashboard_status, "empty")
        self.assertEqual(state.attendance_dashboard_rows, [])

    def test_attendance_pages_expose_required_states_and_routes(self):
        employee_source = inspect.getsource(app_module.ponto)
        manager_source = inspect.getsource(app_module.assiduidade)
        self.assertIn("schedule_summary", employee_source)
        self.assertIn("State.record_attendance_punch", employee_source)
        self.assertIn("State.attendance_dashboard_rows", manager_source)
        self.assertIn('"empty"', manager_source)
        self.assertIn('"error"', manager_source)

        pages = app_module.app._unevaluated_pages
        self.assertEqual(
            pages["ponto"].on_load.fn.__name__, "load_my_attendance"
        )
        self.assertEqual(
            pages["assiduidade"].on_load.fn.__name__,
            "load_attendance_dashboard",
        )


if __name__ == "__main__":
    unittest.main()
