import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "xano" / "table" / "vacation_requests.xs"
VACATION_ENDPOINTS = (
    ROOT / "xano" / "api" / "rh_api" / "vacation_requests_GET.xs",
    ROOT / "xano" / "api" / "rh_api" / "vacation_requests_POST.xs",
    ROOT
    / "xano"
    / "api"
    / "rh_api"
    / "vacation_requests"
    / "vacation_requests_id_GET.xs",
    ROOT
    / "xano"
    / "api"
    / "rh_api"
    / "vacation_requests"
    / "vacation_requests_id_PATCH.xs",
    ROOT
    / "xano"
    / "api"
    / "rh_api"
    / "vacation_requests"
    / "vacation_requests_id_DELETE.xs",
)


class VacationXanoContractTests(unittest.TestCase):
    def test_table_schema_uses_required_employee_dates_and_user_decider(self):
        source = TABLE.read_text(encoding="utf-8")
        self.assertIn("table vacation_requests {", source)
        self.assertIn("int employees_id {", source)
        self.assertIn('table = "employees"', source)
        self.assertIn("date start_date", source)
        self.assertIn("date end_date", source)
        self.assertIn("text status filters=trim", source)
        self.assertIn("int decided_by? {", source)
        self.assertIn('table = "user"', source)
        self.assertNotIn('table = "users"', source)

    def test_every_vacation_endpoint_authorizes_rh_before_data_access(self):
        for endpoint in VACATION_ENDPOINTS:
            with self.subTest(endpoint=endpoint.name):
                source = endpoint.read_text(encoding="utf-8")
                authorization_call = source.index(
                    'function.run "RH API/authorize employee manager"'
                )
                if endpoint == VACATION_ENDPOINTS[4]:
                    self.assertIn('auth = "user"', source)
                    self.assertIn(
                        "authenticated_user_id: $auth.id",
                        source[authorization_call:],
                    )
                    continue
                first_database_access = re.search(
                    r"^\s*db\.(?:query|get|add|patch|del) "
                    r"(?:vacation_requests|employees)\b",
                    source,
                    re.MULTILINE,
                )
                self.assertIn('auth = "user"', source)
                self.assertIsNotNone(first_database_access)
                self.assertLess(authorization_call, first_database_access.start())
                self.assertIn(
                    "authenticated_user_id: $auth.id",
                    source[authorization_call : first_database_access.start()],
                )

    def test_create_endpoint_uses_allowlisted_pending_request_data(self):
        source = VACATION_ENDPOINTS[1].read_text(encoding="utf-8")
        self.assertIn('int employees_id filters=min:1', source)
        self.assertIn("date start_date", source)
        self.assertIn("date end_date", source)
        self.assertIn("$input.start_date <= $input.end_date", source)
        self.assertIn("db.get employees", source)
        self.assertIn('status: "Pendente"', source)
        self.assertNotIn("decided_by: $input", source)
        self.assertNotIn("dblink", source)

    def test_list_endpoint_returns_safe_employee_name_and_request_fields(self):
        source = VACATION_ENDPOINTS[0].read_text(encoding="utf-8")
        self.assertIn('table: "employees"', source)
        self.assertIn('table: "user"', source)
        self.assertIn(
            "where: $db.employee.user_id == $db.employee_user.id", source
        )
        self.assertIn(
            "employee_name: $db.employee_user.name", source
        )
        self.assertNotIn("??", source)
        self.assertIn(
            '"employee_name"',
            source[source.index("output =") :],
        )
        self.assertNotIn("decided_by", source)
        self.assertNotIn("created_at", source)

    def test_decision_endpoint_allows_only_pending_approved_or_rejected(self):
        source = VACATION_ENDPOINTS[3].read_text(encoding="utf-8")
        self.assertIn(
            '$input.status == "Aprovada" || $input.status == "Rejeitada"',
            source,
        )
        self.assertIn('$vacation_request.status == "Pendente"', source)
        self.assertIn("status: $input.status", source)
        self.assertIn("decided_by: $auth.id", source)
        self.assertNotIn("$raw_input", source)
        self.assertNotIn("dblink", source)

    def test_delete_endpoint_is_authorized_but_disables_cancellation(self):
        source = VACATION_ENDPOINTS[4].read_text(encoding="utf-8")
        self.assertIn('auth = "user"', source)
        self.assertIn(
            'function.run "RH API/authorize employee manager"', source
        )
        self.assertIn("precondition (false)", source)
        self.assertNotIn("db.del vacation_requests", source)

    def test_existing_endpoint_guids_are_preserved(self):
        expected_guids = {
            VACATION_ENDPOINTS[0]: "0MbYWxE5wGusg1gHiLdva--U2m4",
            VACATION_ENDPOINTS[1]: "PhMK_KSKsG-cjGbkYIZpzAJ9ZsU",
            VACATION_ENDPOINTS[2]: "WkbTagz1QgKAn3qXDX2UTuRBj3Y",
            VACATION_ENDPOINTS[3]: "TA_AXjgLT-tRtVFxdaY1MzmDhto",
            VACATION_ENDPOINTS[4]: "tQAu7HqSRi_24fGh4d0rBlNfRzg",
        }
        for endpoint, guid in expected_guids.items():
            with self.subTest(endpoint=endpoint.name):
                self.assertIn(
                    f'guid = "{guid}"',
                    endpoint.read_text(encoding="utf-8"),
                )


if __name__ == "__main__":
    unittest.main()
