import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FUNCTION = ROOT / "xano" / "function" / "rh_api" / "authorize_employee_manager.xs"
EVENT_LOG_FUNCTION = (
    ROOT / "xano" / "function" / "getting_started_template" / "create_event_log.xs"
)
EMPLOYEE_ENDPOINTS = (
    ROOT / "xano" / "api" / "rh_api" / "employees_GET.xs",
    ROOT / "xano" / "api" / "rh_api" / "employees_POST.xs",
    ROOT / "xano" / "api" / "rh_api" / "employees" / "employees_id_GET.xs",
    ROOT / "xano" / "api" / "rh_api" / "employees" / "employees_id_PATCH.xs",
    ROOT / "xano" / "api" / "rh_api" / "employees" / "employees_id_DELETE.xs",
)
EMPLOYEE_FORM_OPTIONS_ENDPOINT = (
    ROOT / "xano" / "api" / "rh_api" / "employees_form_options_GET.xs"
)


class EmployeeAuthorizationContractTests(unittest.TestCase):
    def test_authorization_function_checks_authenticated_user_role(self):
        source = FUNCTION.read_text(encoding="utf-8")

        self.assertIn('db.get user {', source)
        self.assertIn('output = ["role"]', source)
        self.assertIn('$authenticated_user.role == "Gestor RH"', source)
        self.assertIn('error_type = "accessdenied"', source)
        self.assertNotIn("db.query users", source)

    def test_user_schema_defines_an_optional_role(self):
        user_schema = (ROOT / "xano" / "table" / "user.xs").read_text(
            encoding="utf-8"
        )

        self.assertIn('text role? filters=trim', user_schema)

    def test_employee_schema_matches_live_table_relationships(self):
        employee_schema = (ROOT / "xano" / "table" / "employees.xs").read_text(
            encoding="utf-8"
        )
        department_schema = (
            ROOT / "xano" / "table" / "departaments.xs"
        ).read_text(encoding="utf-8")

        self.assertIn('text name? filters=trim', employee_schema)
        self.assertIn('table = "user"', employee_schema)
        self.assertIn("int user_id?", employee_schema)
        self.assertIn('int departaments_id?', employee_schema)
        self.assertIn('table = "departaments"', employee_schema)
        self.assertIn("date? admissao?", employee_schema)
        self.assertIn("decimal salario?", employee_schema)
        self.assertNotIn('table = "users"', employee_schema)
        self.assertIn("table departaments {", department_schema)
        self.assertIn("text nome? filters=trim", department_schema)

    def test_event_log_function_writes_only_fields_in_live_table(self):
        function_source = EVENT_LOG_FUNCTION.read_text(encoding="utf-8")
        table_schema = (ROOT / "xano" / "table" / "event_log.xs").read_text(
            encoding="utf-8"
        )

        self.assertIn("db.add event_log {", function_source)
        self.assertIn("user_id: $input.user_id", function_source)
        self.assertIn("action: $input.action", function_source)
        self.assertNotIn('db.add ""', function_source)
        self.assertNotIn("metadata:", function_source)
        self.assertNotIn("account_id:", function_source)
        self.assertIn("int user_id?", table_schema)
        self.assertIn("text action?", table_schema)

    def test_every_employee_endpoint_authenticates_and_authorizes_before_data_access(
        self,
    ):
        for endpoint in EMPLOYEE_ENDPOINTS:
            with self.subTest(endpoint=endpoint.name):
                source = endpoint.read_text(encoding="utf-8")
                authorization_call = source.index(
                    'function.run "RH API/authorize employee manager"'
                )
                first_employee_access = re.search(
                    r"^\s*db\.(?:query|get|add|patch|del) employees\b",
                    source,
                    re.MULTILINE,
                )

                self.assertIn('auth = "user"', source)
                self.assertIsNotNone(first_employee_access)
                self.assertLess(authorization_call, first_employee_access.start())
                self.assertIn(
                    "authenticated_user_id: $auth.id",
                    source[authorization_call : first_employee_access.start()],
                )

    def test_employee_form_options_are_authorized_and_return_only_safe_fields(self):
        source = EMPLOYEE_FORM_OPTIONS_ENDPOINT.read_text(encoding="utf-8")
        self.assertIn('query "employee-form-options" verb=GET', source)
        self.assertNotIn("employees/{employees_id}", source)
        authorization_call = source.index(
            'function.run "RH API/authorize employee manager"'
        )
        department_query = source.index("db.query departaments")

        self.assertIn('auth = "user"', source)
        self.assertLess(authorization_call, department_query)
        self.assertIn('output = ["id", "nome"]', source)
        self.assertIn('table: "employees"', source)
        self.assertIn('type: "left"', source)
        self.assertIn("$db.linked_employee.id == null", source)
        self.assertIn('output = ["id", "name"]', source)
        self.assertNotIn("password", source)
        self.assertNotIn("cpf", source)
        self.assertNotIn("celular", source)

    def test_employee_creation_uses_allowlisted_fields_and_revalidates_links(self):
        source = (
            ROOT / "xano" / "api" / "rh_api" / "employees_POST.xs"
        ).read_text(encoding="utf-8")
        authorization_call = source.index(
            'function.run "RH API/authorize employee manager"'
        )
        department_lookup = source.index("db.get departaments")
        employee_insert = source.index("db.add employees")

        self.assertNotIn('dblink {', source)
        self.assertLess(authorization_call, department_lookup)
        self.assertLess(department_lookup, employee_insert)
        user_lookup = source.index("db.get user")
        duplicate_lookup = source.index("db.query employees")
        self.assertLess(authorization_call, user_lookup)
        self.assertLess(user_lookup, duplicate_lookup)
        self.assertLess(duplicate_lookup, employee_insert)
        self.assertIn("text name filters=trim", source)
        self.assertIn('name: $input.name', source)
        self.assertIn("int user_id filters=min:1", source)
        self.assertIn("user_id: $input.user_id", source)
        self.assertIn("$linked_employee == null", source)
        self.assertIn("departaments_id: $input.departaments_id", source)
        self.assertIn('status: "Ativo"', source)
        self.assertNotIn("salario", source)
        self.assertNotIn("password", source)
        self.assertNotIn("email", source)

    def test_employee_list_includes_records_without_an_associated_user(self):
        source = (
            ROOT / "xano" / "api" / "rh_api" / "employees_GET.xs"
        ).read_text(encoding="utf-8")
        user_join = re.search(
            r"employee_user:\s*\{(?P<body>.*?)\n\s*\}",
            source,
            re.DOTALL,
        )

        self.assertIsNotNone(user_join)
        self.assertIn('table: "user"', user_join.group("body"))
        self.assertIn('type: "left"', user_join.group("body"))
        self.assertIn(
            "$db.employees.name ?? $db.employee_user.name ?? \"Não informado\"",
            source,
        )
