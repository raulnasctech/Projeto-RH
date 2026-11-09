"""Integração autenticada com as jornadas semanais mantidas no Xano."""

import re
from dataclasses import dataclass
from typing import Any

import httpx

REQUEST_TIMEOUT_SECONDS = 12
WEEKDAYS = (
    ("monday", "Segunda-feira"),
    ("tuesday", "Terça-feira"),
    ("wednesday", "Quarta-feira"),
    ("thursday", "Quinta-feira"),
    ("friday", "Sexta-feira"),
    ("saturday", "Sábado"),
    ("sunday", "Domingo"),
)
_TIME_PATTERN = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
_TIME_FIELDS = (
    "start_time",
    "end_time",
    "break_start_time",
    "break_end_time",
)


class WorkScheduleError(Exception):
    """Falha ao consultar, validar ou salvar uma jornada semanal."""


class WorkScheduleAccessDenied(WorkScheduleError):
    """O Xano recusou a operação por falta de permissão."""


@dataclass(frozen=True)
class WorkSchedule:
    id: str
    employee_id: str
    days: list[dict[str, str]]


def empty_work_week() -> list[dict[str, str]]:
    """Retorna os sete dias prontos para o formulário."""
    return [
        {
            "day": day,
            "label": label,
            "is_workday": "false",
            "start_time": "",
            "end_time": "",
            "break_start_time": "",
            "break_end_time": "",
        }
        for day, label in WEEKDAYS
    ]


def _validate_id(value: Any, field: str) -> str:
    if (
        not isinstance(value, (str, int))
        or isinstance(value, bool)
        or not str(value).strip()
    ):
        raise WorkScheduleError(f"A API retornou um identificador inválido para {field}.")
    try:
        parsed_id = int(value)
    except ValueError as error:
        raise WorkScheduleError(
            f"A API retornou um identificador inválido para {field}."
        ) from error
    if parsed_id < 1:
        raise WorkScheduleError(f"A API retornou um identificador inválido para {field}.")
    return str(parsed_id)


def _validate_api_url(api_url: str) -> str:
    normalized_url = api_url.rstrip("/")
    if not normalized_url:
        raise WorkScheduleError(
            "Configure a variável XANO_RH_API_URL para conectar à API de RH."
        )
    return normalized_url


def _authorization_headers(token: str) -> dict[str, str]:
    if not token:
        raise WorkScheduleAccessDenied("Sessão inválida. Entre novamente.")
    return {"Authorization": f"Bearer {token}"}


def _raise_for_response(response: httpx.Response, operation: str) -> None:
    if response.status_code in (401, 403):
        raise WorkScheduleAccessDenied(
            "Seu perfil não tem autorização para gerenciar jornadas."
        )
    if response.is_error:
        raise WorkScheduleError(
            f"Não foi possível {operation} no Xano (HTTP {response.status_code})."
        )


def _parse_response(response: httpx.Response, operation: str) -> Any:
    _raise_for_response(response, operation)
    try:
        return response.json()
    except ValueError as error:
        raise WorkScheduleError(
            "A API retornou uma resposta inválida para jornadas."
        ) from error


def _parse_time(value: Any, field: str) -> str:
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value < 1440:
        raise WorkScheduleError(f"A API retornou um horário inválido para {field}.")
    return f"{value // 60:02d}:{value % 60:02d}"


def _time_to_minutes(value: str, field: str) -> int:
    if not isinstance(value, str) or not _TIME_PATTERN.fullmatch(value):
        raise WorkScheduleError(f"Informe um horário válido para {field}.")
    hours, minutes = (int(part) for part in value.split(":"))
    return hours * 60 + minutes


def _normalize_days(days: Any) -> list[dict[str, str]]:
    if not isinstance(days, list) or len(days) != len(WEEKDAYS):
        raise WorkScheduleError("A jornada deve conter exatamente os sete dias da semana.")

    expected_days = {day for day, _ in WEEKDAYS}
    normalized: dict[str, dict[str, str]] = {}
    labels = dict(WEEKDAYS)
    for day in days:
        if not isinstance(day, dict):
            raise WorkScheduleError("A configuração de um dia da jornada é inválida.")
        name = day.get("day")
        if not isinstance(name, str) or name not in expected_days or name in normalized:
            raise WorkScheduleError("A jornada deve conter cada dia da semana uma única vez.")

        workday_value = day.get("is_workday")
        if workday_value is True or workday_value == "true":
            is_workday = "true"
        elif workday_value is False or workday_value == "false":
            is_workday = "false"
        else:
            raise WorkScheduleError(f"Informe se {labels[name]} é dia trabalhado ou folga.")

        values = {field: day.get(field, "") for field in _TIME_FIELDS}
        if not all(isinstance(value, str) for value in values.values()):
            raise WorkScheduleError(f"Os horários de {labels[name]} são inválidos.")

        if is_workday == "false":
            if any(values.values()):
                raise WorkScheduleError(f"Remova os horários de {labels[name]} configurado como folga.")
        else:
            start = _time_to_minutes(values["start_time"], "entrada")
            end = _time_to_minutes(values["end_time"], "saída")
            if start >= end:
                raise WorkScheduleError(
                    f"A saída de {labels[name]} deve ser posterior à entrada."
                )
            break_start = values["break_start_time"]
            break_end = values["break_end_time"]
            if bool(break_start) != bool(break_end):
                raise WorkScheduleError(
                    f"Informe o início e o fim do intervalo de {labels[name]}."
                )
            if break_start:
                break_start_minutes = _time_to_minutes(break_start, "início do intervalo")
                break_end_minutes = _time_to_minutes(break_end, "fim do intervalo")
                if not start < break_start_minutes < break_end_minutes < end:
                    raise WorkScheduleError(
                        f"O intervalo de {labels[name]} deve ficar entre a entrada e a saída."
                    )

        normalized[name] = {
            "day": name,
            "label": labels[name],
            "is_workday": is_workday,
            **values,
        }

    if set(normalized) != expected_days:
        raise WorkScheduleError("A jornada deve conter cada dia da semana.")
    return [normalized[day] for day, _ in WEEKDAYS]


def _build_schedule_payload(days: Any) -> dict[str, dict[str, Any]]:
    normalized_days = _normalize_days(days)
    payload: dict[str, dict[str, Any]] = {}
    for day in normalized_days:
        is_workday = day["is_workday"] == "true"
        payload[day["day"]] = {
            "is_workday": is_workday,
            "start_minute": (
                _time_to_minutes(day["start_time"], "entrada")
                if is_workday
                else None
            ),
            "end_minute": (
                _time_to_minutes(day["end_time"], "saída")
                if is_workday
                else None
            ),
            "break_start_minute": (
                _time_to_minutes(day["break_start_time"], "início do intervalo")
                if is_workday and day["break_start_time"]
                else None
            ),
            "break_end_minute": (
                _time_to_minutes(day["break_end_time"], "fim do intervalo")
                if is_workday and day["break_end_time"]
                else None
            ),
        }
    return payload


def _parse_schedule(record: Any) -> WorkSchedule:
    if not isinstance(record, dict):
        raise WorkScheduleError("A API retornou uma jornada inválida.")
    weekly_schedule = record.get("weekly_schedule")
    expected_days = {day for day, _ in WEEKDAYS}
    if not isinstance(weekly_schedule, dict) or set(weekly_schedule) != expected_days:
        raise WorkScheduleError("A API retornou uma jornada semanal incompleta.")

    days: list[dict[str, str]] = []
    labels = dict(WEEKDAYS)
    for day_name, _ in WEEKDAYS:
        day = weekly_schedule[day_name]
        if not isinstance(day, dict) or not isinstance(day.get("is_workday"), bool):
            raise WorkScheduleError("A API retornou uma configuração de dia inválida.")
        is_workday = day["is_workday"]
        parsed_day = {
            "day": day_name,
            "label": labels[day_name],
            "is_workday": "true" if is_workday else "false",
        }
        for source_field, target_field in (
            ("start_minute", "start_time"),
            ("end_minute", "end_time"),
            ("break_start_minute", "break_start_time"),
            ("break_end_minute", "break_end_time"),
        ):
            value = day.get(source_field)
            if value is None:
                parsed_day[target_field] = ""
            else:
                parsed_day[target_field] = _parse_time(value, target_field)
        days.append(parsed_day)

    normalized_days = _normalize_days(days)
    return WorkSchedule(
        id=_validate_id(record.get("id"), "jornada"),
        employee_id=_validate_id(record.get("employees_id"), "colaborador"),
        days=normalized_days,
    )


async def get_work_schedule(
    api_url: str, token: str, employee_id: str
) -> WorkSchedule | None:
    """Consulta uma jornada; ausência é diferente de falha de consulta."""
    normalized_url = _validate_api_url(api_url)
    parsed_employee_id = _validate_id(employee_id, "colaborador")
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.get(
            f"{normalized_url}/work_schedules/{parsed_employee_id}",
            headers=_authorization_headers(token),
        )
    data = _parse_response(response, "consultar a jornada")
    if data is None:
        return None
    schedule = _parse_schedule(data)
    if schedule.employee_id != parsed_employee_id:
        raise WorkScheduleError("A API retornou uma jornada de outro colaborador.")
    return schedule


async def save_work_schedule(
    api_url: str,
    token: str,
    employee_id: str,
    days: Any,
    schedule_id: str = "",
) -> WorkSchedule:
    """Cria ou substitui uma semana completa em uma única requisição."""
    normalized_url = _validate_api_url(api_url)
    parsed_employee_id = _validate_id(employee_id, "colaborador")
    payload = _build_schedule_payload(days)
    headers = _authorization_headers(token)
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        if schedule_id:
            parsed_schedule_id = _validate_id(schedule_id, "jornada")
            response = await client.patch(
                f"{normalized_url}/work_schedules/{parsed_schedule_id}",
                headers=headers,
                json={"weekly_schedule": payload},
            )
        else:
            response = await client.post(
                f"{normalized_url}/work_schedules",
                headers=headers,
                json={
                    "employees_id": int(parsed_employee_id),
                    "weekly_schedule": payload,
                },
            )

    data = _parse_response(response, "salvar a jornada")
    schedule = _parse_schedule(data)
    if schedule.employee_id != parsed_employee_id:
        raise WorkScheduleError("A API confirmou uma jornada de outro colaborador.")
    return schedule
