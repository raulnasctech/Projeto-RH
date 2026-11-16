import unittest
from unittest.mock import patch

import httpx

from Gestao_RH_Impacta import attendance_service


WORK_DATE = "2026-11-09"
SERVER_NOW = "2026-11-09T10:00:00-03:00"
EMPLOYEE = {
    "id": 7,
    "employee_name": "Ana Souza",
    "job_title": "Analista",
    "department": "Produto",
    "status": "Ativo",
}
SCHEDULE_WITH_BREAK = {
    "is_workday": True,
    "start_minute": 540,
    "end_minute": 1020,
    "break_start_minute": 720,
    "break_end_minute": 780,
}
SCHEDULE_WITHOUT_BREAK = {
    "is_workday": True,
    "start_minute": 540,
    "end_minute": 1020,
    "break_start_minute": None,
    "break_end_minute": None,
}


def event(punch_type, time_value, schedule_snapshot=None):
    return {
        "punch_type": punch_type,
        "punched_at": f"{WORK_DATE}T{time_value}:00-03:00",
        "schedule_snapshot": schedule_snapshot,
    }


def my_attendance(schedule, punches, server_now=SERVER_NOW):
    return {
        "employee": EMPLOYEE,
        "work_date": WORK_DATE,
        "server_now": server_now,
        "schedule": schedule,
        "punches": punches,
    }


class FakeAsyncClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False

    async def get(self, url, **kwargs):
        self.calls.append(("get", url, kwargs))
        if isinstance(self.response, Exception):
            raise self.response
        return self.response

    async def post(self, url, **kwargs):
        self.calls.append(("post", url, kwargs))
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


class AttendanceServiceTests(unittest.TestCase):
    def test_employee_without_interval_has_two_punches(self):
        row = attendance_service._build_day(
            EMPLOYEE,
            SCHEDULE_WITHOUT_BREAK,
            [event("entry", "09:02")],
            attendance_service._parse_server_time(SERVER_NOW),
            attendance_service._parse_work_date(WORK_DATE),
        )

        self.assertEqual(row.state, "Ponto aberto")
        self.assertEqual(row.next_punch, "exit")
        self.assertEqual(row.next_punch_label, "Saída final")
        self.assertIn("Entrada 09:00", row.schedule_summary)
        self.assertIn("Saída final 17:00", row.schedule_summary)
        self.assertFalse(row.can_punch)

        row = attendance_service._build_day(
            EMPLOYEE,
            SCHEDULE_WITHOUT_BREAK,
            [event("entry", "09:02"), event("exit", "17:01")],
            attendance_service._parse_server_time("2026-11-09T17:02:00-03:00"),
            attendance_service._parse_work_date(WORK_DATE),
        )
        self.assertEqual(row.state, "Concluído")
        self.assertEqual(row.as_dict()["entry_at"], "09:02")
        self.assertEqual(row.as_dict()["exit_at"], "17:01")

    def test_employee_with_interval_has_four_ordered_punches(self):
        punches = [
            event("entry", "09:01"),
            event("break_start", "12:02"),
            event("break_end", "13:03"),
            event("exit", "17:04"),
        ]
        row = attendance_service._build_day(
            EMPLOYEE,
            SCHEDULE_WITH_BREAK,
            punches,
            attendance_service._parse_server_time("2026-11-09T17:05:00-03:00"),
            attendance_service._parse_work_date(WORK_DATE),
        )

        self.assertEqual(row.state, "Concluído")
        self.assertEqual(row.next_punch, "")
        self.assertEqual(row.as_dict()["break_start_at"], "12:02")
        self.assertEqual(row.as_dict()["break_end_at"], "13:03")
        self.assertIn("Retorno do intervalo 13:00", row.as_dict()["schedule_summary"])

    def test_missing_and_late_punches_have_distinct_states(self):
        parsed_date = attendance_service._parse_work_date(WORK_DATE)
        row = attendance_service._build_day(
            EMPLOYEE,
            SCHEDULE_WITH_BREAK,
            [],
            attendance_service._parse_server_time("2026-11-09T08:59:00-03:00"),
            parsed_date,
        )
        self.assertEqual(row.state, "Aguardando horário")
        self.assertFalse(row.can_punch)

        row = attendance_service._build_day(
            EMPLOYEE,
            SCHEDULE_WITH_BREAK,
            [],
            attendance_service._parse_server_time("2026-11-09T09:00:00-03:00"),
            parsed_date,
        )
        self.assertEqual(row.state, "Não iniciou")
        self.assertTrue(row.can_punch)

        row = attendance_service._build_day(
            EMPLOYEE,
            SCHEDULE_WITH_BREAK,
            [event("entry", "09:08")],
            attendance_service._parse_server_time("2026-11-09T12:00:00-03:00"),
            parsed_date,
        )
        self.assertEqual(row.state, "Incompleto")
        self.assertEqual(row.next_punch, "break_start")
        self.assertTrue(row.can_punch)

    def test_rest_day_and_missing_schedule_are_not_absences(self):
        parsed_date = attendance_service._parse_work_date(WORK_DATE)
        rest_schedule = {"is_workday": False}
        row = attendance_service._build_day(
            EMPLOYEE,
            rest_schedule,
            [],
            attendance_service._parse_server_time(SERVER_NOW),
            parsed_date,
        )
        self.assertEqual(row.state, "Folga")
        self.assertEqual(row.next_punch, "")

        row = attendance_service._build_day(
            EMPLOYEE,
            None,
            [],
            attendance_service._parse_server_time(SERVER_NOW),
            parsed_date,
        )
        self.assertEqual(row.state, "Jornada não cadastrada")

    def test_schedule_accepts_boolean_and_string_workday_values(self):
        parsed_date = attendance_service._parse_work_date(WORK_DATE)
        server_time = attendance_service._parse_server_time(SERVER_NOW)

        for is_workday in (True, "true"):
            with self.subTest(is_workday=is_workday):
                schedule = {
                    **SCHEDULE_WITHOUT_BREAK,
                    "is_workday": is_workday,
                }
                row = attendance_service._build_day(
                    EMPLOYEE, schedule, [], server_time, parsed_date
                )
                self.assertEqual(
                    row.schedule_summary, "Entrada 09:00; Saída final 17:00"
                )

        for is_workday in (False, "false"):
            with self.subTest(is_workday=is_workday):
                row = attendance_service._build_day(
                    EMPLOYEE,
                    {"is_workday": is_workday},
                    [],
                    server_time,
                    parsed_date,
                )
                self.assertEqual(row.state, "Folga")

    def test_invalid_schedule_error_identifies_shape_without_values(self):
        with self.assertRaisesRegex(
            attendance_service.AttendanceError,
            "campo is_workday ausente; chaves recebidas: start_time",
        ):
            attendance_service._parse_day_schedule({"start_time": "09:00"})

        with self.assertRaisesRegex(
            attendance_service.AttendanceError,
            "tipo recebido: str",
        ):
            attendance_service._parse_day_schedule("invalid")

    def test_rejects_malformed_schedule_and_out_of_order_punches(self):
        with self.assertRaises(attendance_service.AttendanceError):
            attendance_service._build_day(
                EMPLOYEE,
                {**SCHEDULE_WITH_BREAK, "break_end_minute": 720},
                [],
                attendance_service._parse_server_time(SERVER_NOW),
                attendance_service._parse_work_date(WORK_DATE),
            )
        with self.assertRaises(attendance_service.AttendanceError):
            attendance_service._build_day(
                EMPLOYEE,
                SCHEDULE_WITH_BREAK,
                [event("entry", "09:01"), event("break_end", "13:01")],
                attendance_service._parse_server_time(SERVER_NOW),
                attendance_service._parse_work_date(WORK_DATE),
            )

    def test_dashboard_uses_saved_day_schedule_and_excludes_inactive(self):
        data = {
            "work_date": WORK_DATE,
            "server_now": SERVER_NOW,
            "employees": [
                {
                    **EMPLOYEE,
                    "weekly_schedule": {"monday": SCHEDULE_WITHOUT_BREAK},
                }
            ],
            "punches": [
                {
                    "employees_id": 7,
                    **event("entry", "09:02", SCHEDULE_WITH_BREAK),
                }
            ],
        }

        rows = attendance_service._parse_dashboard(data)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].next_punch, "break_start")
        self.assertEqual(rows[0].state, "Ponto aberto")

        data["punches"].append(
            {"employees_id": 99, **event("entry", "09:02")}
        )
        with self.assertRaises(attendance_service.AttendanceError):
            attendance_service._parse_dashboard(data)

    def test_employee_attendance_selects_day_from_weekly_schedule_response(self):
        weekly_schedule = {
            day: {"is_workday": False}
            for day in attendance_service.WEEKDAYS
        }
        weekly_schedule["monday"] = SCHEDULE_WITHOUT_BREAK
        data = my_attendance(weekly_schedule, [])

        row = attendance_service._parse_my_attendance(data)

        self.assertIn("Entrada 09:00", row.schedule_summary)
        self.assertEqual(row.state, "Não iniciou")


class AttendanceApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_gets_own_attendance_without_employee_identifier(self):
        client = FakeAsyncClient(
            httpx.Response(200, json=my_attendance(SCHEDULE_WITHOUT_BREAK, []))
        )
        with patch.object(
            attendance_service.httpx, "AsyncClient", return_value=client
        ):
            row = await attendance_service.get_my_attendance(
                "https://example.xano.io/api:rh/", "fixture-token"
            )

        self.assertEqual(row.employee_id, "7")
        self.assertEqual(
            client.calls[0][1],
            "https://example.xano.io/api:rh/attendance/me",
        )
        self.assertEqual(
            client.calls[0][2]["headers"]["Authorization"],
            "Bearer fixture-token",
        )

    async def test_post_does_not_send_identity_date_or_punch_time(self):
        client = FakeAsyncClient(
            httpx.Response(
                200,
                json=my_attendance(
                    SCHEDULE_WITHOUT_BREAK,
                    [event("entry", "09:05")],
                ),
            )
        )
        with patch.object(
            attendance_service.httpx, "AsyncClient", return_value=client
        ):
            row = await attendance_service.record_next_punch(
                "https://example.xano.io/api:rh", "fixture-token"
            )

        self.assertEqual(row.punches[0]["type"], "entry")
        self.assertEqual(client.calls[0][0], "post")
        self.assertEqual(client.calls[0][2]["json"], {})

    async def test_reports_access_denied_and_malformed_api_response(self):
        client = FakeAsyncClient(
            httpx.Response(403, json={"message": "secret"})
        )
        with (
            patch.object(
                attendance_service.httpx, "AsyncClient", return_value=client
            ),
            self.assertRaises(
                attendance_service.AttendanceAccessDenied
            ) as error,
        ):
            await attendance_service.get_my_attendance(
                "https://example.xano.io/api:rh", "fixture-token"
            )
        self.assertNotIn("secret", str(error.exception))

        client = FakeAsyncClient(
            httpx.Response(200, json={"unexpected": True})
        )
        with (
            patch.object(
                attendance_service.httpx, "AsyncClient", return_value=client
            ),
            self.assertRaises(attendance_service.AttendanceError),
        ):
            await attendance_service.get_my_attendance(
                "https://example.xano.io/api:rh", "fixture-token"
            )

    async def test_explains_employee_link_and_manager_role_denials(self):
        cases = (
            (
                "A conta deve estar vinculada a exatamente um colaborador.",
                "vinculada a exatamente um colaborador ativo",
            ),
            (
                "Somente colaboradores ativos podem acessar o ponto.",
                "cadastro vinculado à sua conta não está ativo",
            ),
            (
                "Acesso negado.",
                "restrito ao perfil Gestor RH",
            ),
        )
        for backend_message, expected_message in cases:
            with self.subTest(backend_message=backend_message):
                client = FakeAsyncClient(
                    httpx.Response(403, json={"message": backend_message})
                )
                with (
                    patch.object(
                        attendance_service.httpx,
                        "AsyncClient",
                        return_value=client,
                    ),
                    self.assertRaises(
                        attendance_service.AttendanceAccessDenied
                    ) as error,
                ):
                    await attendance_service.get_my_attendance(
                        "https://example.xano.io/api:rh", "fixture-token"
                    )
                self.assertIn(expected_message, str(error.exception))

    async def test_expired_attendance_session_has_a_specific_message(self):
        client = FakeAsyncClient(httpx.Response(401, json={}))
        with (
            patch.object(
                attendance_service.httpx, "AsyncClient", return_value=client
            ),
            self.assertRaisesRegex(
                attendance_service.AttendanceAccessDenied,
                "sessão do Xano expirou",
            ),
        ):
            await attendance_service.get_my_attendance(
                "https://example.xano.io/api:rh", "fixture-token"
            )

    async def test_explains_when_attendance_endpoint_is_not_published(self):
        client = FakeAsyncClient(httpx.Response(404, json={"message": "Not found"}))
        with patch.object(
            attendance_service.httpx, "AsyncClient", return_value=client
        ):
            with self.assertRaisesRegex(
                attendance_service.AttendanceError,
                "rotas /attendance/me.*XANO_RH_API_URL",
            ):
                await attendance_service.get_my_attendance(
                    "https://example.xano.io/api:rh", "fixture-token"
                )


if __name__ == "__main__":
    unittest.main()
