import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "xano" / "table" / "attendance_punches.xs"
CLOCK = ROOT / "xano" / "function" / "rh_api" / "get_attendance_clock.xs"
ME_ENDPOINT = ROOT / "xano" / "api" / "rh_api" / "attendance" / "me_GET.xs"
PUNCH_ENDPOINT = (
    ROOT
    / "xano"
    / "api"
    / "rh_api"
    / "attendance"
    / "me"
    / "punch_POST.xs"
)
TODAY_ENDPOINT = (
    ROOT / "xano" / "api" / "rh_api" / "attendance" / "today_GET.xs"
)


class AttendanceXanoContractTests(unittest.TestCase):
    def test_punch_events_have_unique_employee_date_and_type(self):
        source = TABLE.read_text(encoding="utf-8")
        self.assertIn("table attendance_punches {", source)
        self.assertIn('table = "employees"', source)
        self.assertIn("date work_date", source)
        self.assertIn("text punch_type", source)
        self.assertIn("timestamp punched_at?=now", source)
        self.assertIn("json? schedule_snapshot?", source)
        for field in ("employees_id", "work_date", "punch_type"):
            self.assertIn(f'{{name: "{field}", op: "asc"}}', source)
        self.assertIn('type : "btree|unique"', source)

    def test_server_clock_uses_sao_paulo_timezone_and_no_client_clock(self):
        source = CLOCK.read_text(encoding="utf-8")
        self.assertIn("format_timestamp", source)
        self.assertIn('"America/Sao_Paulo"', source)
        self.assertIn("value = now", source)
        self.assertNotIn("$input.", source)

    def test_employee_endpoints_resolve_identity_from_authenticated_session(self):
        for endpoint in (ME_ENDPOINT, PUNCH_ENDPOINT):
            with self.subTest(endpoint=endpoint.name):
                source = endpoint.read_text(encoding="utf-8")
                self.assertIn('auth = "user"', source)
                self.assertIn("$db.employees.user_id == $auth.id", source)
                self.assertIn("($linked_employees|count) == 1", source)
                self.assertIn('($employee.status|lower) == "ativo"', source)
                self.assertNotIn("employees_id?", source)
                self.assertNotIn("work_date?", source)
                self.assertNotIn("punch_type?", source)

    def test_employee_attendance_read_handles_missing_schedule(self):
        source = ME_ENDPOINT.read_text(encoding="utf-8")
        lookup = source.index("db.get work_schedules")
        schedule_day = source.index("var $schedule_day")
        guarded_read = source.index(
            "if ($work_schedule != null)", schedule_day
        )
        dereference = source.index(
            "$work_schedule.weekly_schedule|get:$clock.weekday"
        )
        self.assertLess(lookup, schedule_day)
        self.assertLess(schedule_day, guarded_read)
        self.assertLess(guarded_read, dereference)
        self.assertIn("value = null", source[schedule_day:guarded_read])

    def test_punch_endpoint_uses_expected_order_and_server_timestamp(self):
        source = PUNCH_ENDPOINT.read_text(encoding="utf-8")
        self.assertIn('$clock.current_minute >= $schedule_day.start_minute', source)
        self.assertIn('$clock.current_minute >= $schedule_day.break_start_minute', source)
        self.assertIn('$clock.current_minute >= $schedule_day.break_end_minute', source)
        self.assertIn('$clock.current_minute >= $schedule_day.end_minute', source)
        self.assertIn('punch_type: "entry"', source)
        self.assertIn('schedule_snapshot: $schedule_day', source)
        self.assertIn('error = "As batidas existentes estão incompletas ou fora de ordem."', source)
        self.assertIn('punch_type: "break_start"', source)
        self.assertIn('punch_type: "break_end"', source)
        self.assertIn('punch_type: "exit"', source)
        self.assertNotIn("$input.", source)

    def test_manager_dashboard_authorizes_before_access_and_limits_active_rows(self):
        source = TODAY_ENDPOINT.read_text(encoding="utf-8")
        authorization = source.index(
            'function.run "RH API/authorize employee manager"'
        )
        first_database_access = source.index("db.")
        self.assertIn('auth = "user"', source)
        self.assertLess(authorization, first_database_access)
        self.assertIn('($db.employees.status|lower) == "ativo"', source)
        self.assertIn("employee_name: $db.employee_user.name", source)
        self.assertNotIn("$db.$db.employee_user", source)
        self.assertIn("$clock.work_date", source)
        self.assertNotIn("salario", source)
        self.assertNotIn("$input.", source)


if __name__ == "__main__":
    unittest.main()
