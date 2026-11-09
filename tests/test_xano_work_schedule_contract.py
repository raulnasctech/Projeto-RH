import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "xano" / "table" / "work_schedules.xs"
VALIDATE_SCHEDULE = (
    ROOT / "xano" / "function" / "rh_api" / "validate_work_schedule.xs"
)
VALIDATE_DAY = (
    ROOT / "xano" / "function" / "rh_api" / "validate_work_schedule_day.xs"
)
ENDPOINTS = (
    ROOT
    / "xano"
    / "api"
    / "rh_api"
    / "work_schedules"
    / "employees_id_GET.xs",
    ROOT / "xano" / "api" / "rh_api" / "work_schedules_POST.xs",
    ROOT
    / "xano"
    / "api"
    / "rh_api"
    / "work_schedules"
    / "work_schedules_id_PATCH.xs",
)


class WorkScheduleXanoContractTests(unittest.TestCase):
    def test_table_stores_one_week_per_employee_with_unique_relationship(self):
        source = TABLE.read_text(encoding="utf-8")
        self.assertIn("table work_schedules {", source)
        self.assertIn("int employees_id {", source)
        self.assertIn('table = "employees"', source)
        self.assertIn("json weekly_schedule", source)
        self.assertIn('type : "btree|unique"', source)
        self.assertIn('{name: "employees_id", op: "asc"}', source)

    def test_schedule_validation_requires_all_seven_days(self):
        source = VALIDATE_SCHEDULE.read_text(encoding="utf-8")
        for day in (
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ):
            with self.subTest(day=day):
                self.assertIn(f"$input.weekly_schedule.{day} != null", source)
                self.assertIn(
                    f"function.run \"RH API/validate work schedule day\"",
                    source,
                )
        self.assertIn("Informe a configuração para os sete dias", source)

    def test_day_validation_enforces_work_rest_and_interval_order(self):
        source = VALIDATE_DAY.read_text(encoding="utf-8")
        self.assertIn("$input.start_minute < 1440", source)
        self.assertIn("$input.end_minute > $input.start_minute", source)
        self.assertIn("$input.break_start_minute > $input.start_minute", source)
        self.assertIn("$input.break_end_minute > $input.break_start_minute", source)
        self.assertIn("$input.break_end_minute < $input.end_minute", source)
        self.assertIn("$input.is_workday == false", source)
        self.assertIn("$input.break_start_minute == null", source)
        self.assertIn("$input.break_end_minute == null", source)

    def test_all_endpoints_authorize_before_schedule_data_access(self):
        for endpoint in ENDPOINTS:
            with self.subTest(endpoint=endpoint.name):
                source = endpoint.read_text(encoding="utf-8")
                authorization = source.index(
                    'function.run "RH API/authorize employee manager"'
                )
                first_database_access = source.index("db.")
                self.assertIn('auth = "user"', source)
                self.assertLess(authorization, first_database_access)
                self.assertIn(
                    "authenticated_user_id: $auth.id",
                    source[authorization:first_database_access],
                )

    def test_create_and_update_validate_before_single_write(self):
        for endpoint, write_statement in (
            (ENDPOINTS[1], "db.add work_schedules"),
            (ENDPOINTS[2], "db.patch work_schedules"),
        ):
            with self.subTest(endpoint=endpoint.name):
                source = endpoint.read_text(encoding="utf-8")
                validation = source.index(
                    'function.run "RH API/validate work schedule"'
                )
                write = source.index(write_statement)
                self.assertLess(validation, write)
                self.assertEqual(source.count(write_statement), 1)
                self.assertNotIn("db.del work_schedules", source)
                self.assertNotIn("util.get_raw_input", source)


if __name__ == "__main__":
    unittest.main()
