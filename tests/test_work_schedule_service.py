import unittest
from unittest.mock import patch

import httpx

from Gestao_RH_Impacta import work_schedule_service
from Gestao_RH_Impacta.work_schedule_service import (
    WorkSchedule,
    WorkScheduleAccessDenied,
    WorkScheduleError,
    empty_work_week,
)


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

    async def patch(self, url, **kwargs):
        self.calls.append(("patch", url, kwargs))
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


def valid_work_week():
    days = empty_work_week()
    days[0].update(
        is_workday="true",
        start_time="08:00",
        end_time="17:00",
        break_start_time="12:00",
        break_end_time="13:00",
    )
    return days


def schedule_record():
    days = {
        day["day"]: {
            "is_workday": day["is_workday"] == "true",
            "start_minute": (
                480 if day["is_workday"] == "true" else None
            ),
            "end_minute": (
                1020 if day["is_workday"] == "true" else None
            ),
            "break_start_minute": (
                720 if day["is_workday"] == "true" else None
            ),
            "break_end_minute": (
                780 if day["is_workday"] == "true" else None
            ),
        }
        for day in valid_work_week()
    }
    return {"id": 12, "employees_id": 3, "weekly_schedule": days}


class WorkScheduleServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_gets_schedule_with_auth_and_parsed_times(self):
        client = FakeAsyncClient(httpx.Response(200, json=schedule_record()))
        with patch.object(
            work_schedule_service.httpx, "AsyncClient", return_value=client
        ):
            schedule = await work_schedule_service.get_work_schedule(
                "https://example.xano.io/api:rh/", "fixture-token", "3"
            )

        self.assertIsInstance(schedule, WorkSchedule)
        self.assertEqual(schedule.id, "12")
        self.assertEqual(schedule.employee_id, "3")
        self.assertEqual(schedule.days[0]["start_time"], "08:00")
        self.assertEqual(schedule.days[0]["break_end_time"], "13:00")
        self.assertEqual(schedule.days[1]["is_workday"], "false")
        self.assertEqual(
            client.calls[0],
            (
                "get",
                "https://example.xano.io/api:rh/work_schedules/3",
                {
                    "headers": {"Authorization": "Bearer fixture-token"},
                },
            ),
        )

    async def test_missing_schedule_is_distinct_from_failed_request(self):
        client = FakeAsyncClient(
            httpx.Response(200, content=b"null", headers={"content-type": "application/json"})
        )
        with patch.object(
            work_schedule_service.httpx, "AsyncClient", return_value=client
        ):
            schedule = await work_schedule_service.get_work_schedule(
                "https://example.xano.io/api:rh", "fixture-token", "3"
            )
        self.assertIsNone(schedule)

    async def test_creates_complete_week_as_one_json_payload(self):
        client = FakeAsyncClient(httpx.Response(200, json=schedule_record()))
        with patch.object(
            work_schedule_service.httpx, "AsyncClient", return_value=client
        ):
            schedule = await work_schedule_service.save_work_schedule(
                "https://example.xano.io/api:rh",
                "fixture-token",
                "3",
                valid_work_week(),
            )

        self.assertEqual(schedule.id, "12")
        method, url, kwargs = client.calls[0]
        self.assertEqual(method, "post")
        self.assertEqual(url, "https://example.xano.io/api:rh/work_schedules")
        self.assertEqual(kwargs["json"]["employees_id"], 3)
        monday = kwargs["json"]["weekly_schedule"]["monday"]
        self.assertEqual(
            monday,
            {
                "is_workday": True,
                "start_minute": 480,
                "end_minute": 1020,
                "break_start_minute": 720,
                "break_end_minute": 780,
            },
        )
        self.assertIsNone(kwargs["json"]["weekly_schedule"]["sunday"]["start_minute"])

    async def test_updates_existing_schedule_in_one_patch(self):
        client = FakeAsyncClient(httpx.Response(200, json=schedule_record()))
        with patch.object(
            work_schedule_service.httpx, "AsyncClient", return_value=client
        ):
            await work_schedule_service.save_work_schedule(
                "https://example.xano.io/api:rh",
                "fixture-token",
                "3",
                valid_work_week(),
                schedule_id="12",
            )

        self.assertEqual(client.calls[0][0], "patch")
        self.assertEqual(
            client.calls[0][1],
            "https://example.xano.io/api:rh/work_schedules/12",
        )
        self.assertEqual(set(client.calls[0][2]["json"]), {"weekly_schedule"})

    async def test_rejects_invalid_weeks_before_request(self):
        cases = []
        missing_day = valid_work_week()[:-1]
        cases.append(missing_day)

        duplicate_day = valid_work_week()
        duplicate_day[-1]["day"] = duplicate_day[0]["day"]
        cases.append(duplicate_day)

        missing_end = valid_work_week()
        missing_end[0]["end_time"] = ""
        cases.append(missing_end)

        reversed_shift = valid_work_week()
        reversed_shift[0]["end_time"] = "07:59"
        cases.append(reversed_shift)

        partial_break = valid_work_week()
        partial_break[0]["break_end_time"] = ""
        cases.append(partial_break)

        reversed_break = valid_work_week()
        reversed_break[0]["break_start_time"] = "13:00"
        reversed_break[0]["break_end_time"] = "12:00"
        cases.append(reversed_break)

        off_day_with_time = empty_work_week()
        off_day_with_time[0]["start_time"] = "08:00"
        cases.append(off_day_with_time)

        client = FakeAsyncClient(httpx.Response(200, json=schedule_record()))
        for days in cases:
            with (
                self.subTest(days=days),
                patch.object(
                    work_schedule_service.httpx, "AsyncClient", return_value=client
                ),
                self.assertRaises(WorkScheduleError),
            ):
                await work_schedule_service.save_work_schedule(
                    "https://example.xano.io/api:rh",
                    "fixture-token",
                    "3",
                    days,
                )
        self.assertEqual(client.calls, [])

    async def test_rejects_malformed_response_and_other_employee_schedule(self):
        for payload in (
            {"id": 1, "employees_id": 3, "weekly_schedule": {}},
            {**schedule_record(), "id": 0},
            {**schedule_record(), "employees_id": 4},
        ):
            client = FakeAsyncClient(httpx.Response(200, json=payload))
            with (
                self.subTest(payload=payload),
                patch.object(
                    work_schedule_service.httpx, "AsyncClient", return_value=client
                ),
                self.assertRaises(WorkScheduleError),
            ):
                await work_schedule_service.get_work_schedule(
                    "https://example.xano.io/api:rh", "fixture-token", "3"
                )

    async def test_reports_http_and_access_denied_errors(self):
        for response, error_type in (
            (
                httpx.Response(
                    403, json={"message": "secret authorization details"}
                ),
                WorkScheduleAccessDenied,
            ),
            (
                httpx.Response(500, json={"message": "secret backend details"}),
                WorkScheduleError,
            ),
        ):
            client = FakeAsyncClient(response)
            with (
                self.subTest(status=response.status_code),
                patch.object(
                    work_schedule_service.httpx, "AsyncClient", return_value=client
                ),
                self.assertRaises(error_type) as raised,
            ):
                await work_schedule_service.get_work_schedule(
                    "https://example.xano.io/api:rh", "fixture-token", "3"
                )
            self.assertNotIn("secret", str(raised.exception))

    async def test_reports_network_failure_without_success_fallback(self):
        client = FakeAsyncClient(httpx.ConnectError("offline"))
        with (
            patch.object(
                work_schedule_service.httpx, "AsyncClient", return_value=client
            ),
            self.assertRaises(httpx.ConnectError),
        ):
            await work_schedule_service.get_work_schedule(
                "https://example.xano.io/api:rh", "fixture-token", "3"
            )


if __name__ == "__main__":
    unittest.main()
