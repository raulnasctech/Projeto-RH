"""Integração autenticada e cálculo dos estados diários de ponto."""

from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from typing import Any
from zoneinfo import ZoneInfo

import httpx


REQUEST_TIMEOUT_SECONDS = 12
OPERATIONAL_TIMEZONE = ZoneInfo("America/Sao_Paulo")
PUNCH_LABELS = {
    "entry": "Entrada",
    "break_start": "Saída para intervalo",
    "break_end": "Retorno do intervalo",
    "exit": "Saída final",
}
WEEKDAYS = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)


class AttendanceError(Exception):
    """Falha ao consultar, validar ou registrar ponto."""


class AttendanceAccessDenied(AttendanceError):
    """O Xano recusou a operação por falta de permissão."""


@dataclass(frozen=True)
class AttendanceDay:
    employee_id: str
    employee_name: str
    job_title: str
    department: str
    status: str
    state: str
    schedule_summary: str
    next_punch: str
    next_punch_label: str
    next_punch_at: str
    can_punch: bool
    punches: list[dict[str, str]]

    def as_dict(self) -> dict[str, str]:
        row = {
            "employee_id": self.employee_id,
            "employee_name": self.employee_name,
            "job_title": self.job_title,
            "department": self.department,
            "status": self.status,
            "state": self.state,
            "schedule_summary": self.schedule_summary,
            "next_punch": self.next_punch,
            "next_punch_label": self.next_punch_label,
            "next_punch_at": self.next_punch_at,
            "can_punch": "true" if self.can_punch else "false",
            "entry_at": "",
            "break_start_at": "",
            "break_end_at": "",
            "exit_at": "",
        }
        for punch in self.punches:
            row[f"{punch['type']}_at"] = punch["at"]
        return row


def _validate_api_url(api_url: str) -> str:
    normalized_url = api_url.rstrip("/")
    if not normalized_url:
        raise AttendanceError(
            "Configure a variável XANO_RH_API_URL para conectar à API de RH."
        )
    return normalized_url


def _authorization_headers(token: str) -> dict[str, str]:
    if not token:
        raise AttendanceAccessDenied("Sessão inválida. Entre novamente.")
    return {"Authorization": f"Bearer {token}"}


def _raise_for_response(response: httpx.Response, operation: str) -> None:
    if response.status_code == 401:
        raise AttendanceAccessDenied(
            "Sua sessão do Xano expirou. Saia da conta e entre novamente."
        )
    if response.status_code == 403:
        try:
            data = response.json()
        except ValueError:
            data = {}
        backend_message = data.get("message") if isinstance(data, dict) else None
        if backend_message == (
            "A conta deve estar vinculada a exatamente um colaborador."
        ):
            raise AttendanceAccessDenied(
                "Esta conta não está vinculada a exatamente um colaborador ativo. "
                "Peça ao Gestor RH para vincular a conta ao cadastro do funcionário."
            )
        if backend_message == (
            "Somente colaboradores ativos podem acessar o ponto."
        ) or backend_message == (
            "Somente colaboradores ativos podem registrar ponto."
        ):
            raise AttendanceAccessDenied(
                "O cadastro vinculado à sua conta não está ativo. "
                "Peça ao Gestor RH para verificar a situação do funcionário."
            )
        if backend_message == "Acesso negado.":
            raise AttendanceAccessDenied(
                "O painel de ponto é restrito ao perfil Gestor RH. "
                "Confirme se o perfil da sua conta está como Gestor RH no Xano."
            )
        raise AttendanceAccessDenied(
            "Seu perfil ou vínculo não tem autorização para acessar o ponto."
        )
    if response.status_code == 404:
        raise AttendanceError(
            f"O endpoint de ponto não foi encontrado ao tentar {operation}. "
            "Confirme se as rotas /attendance/me, /attendance/me/punch e "
            "/attendance/today foram publicadas no grupo configurado em "
            "XANO_RH_API_URL."
        )
    if response.is_error:
        raise AttendanceError(
            f"Não foi possível {operation} no Xano (HTTP {response.status_code})."
        )


def _parse_response(response: httpx.Response, operation: str) -> Any:
    _raise_for_response(response, operation)
    try:
        return response.json()
    except ValueError as error:
        raise AttendanceError(
            "A API retornou uma resposta inválida para ponto."
        ) from error


def _parse_id(value: Any, field: str) -> str:
    if (
        not isinstance(value, (str, int))
        or isinstance(value, bool)
        or not str(value).strip()
    ):
        raise AttendanceError(f"A API retornou um identificador inválido para {field}.")
    try:
        parsed_id = int(value)
    except ValueError as error:
        raise AttendanceError(
            f"A API retornou um identificador inválido para {field}."
        ) from error
    if parsed_id < 1:
        raise AttendanceError(f"A API retornou um identificador inválido para {field}.")
    return str(parsed_id)


def _parse_server_time(value: Any) -> datetime:
    try:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            epoch_seconds = value / 1000 if abs(value) >= 100_000_000_000 else value
            return datetime.fromtimestamp(epoch_seconds, tz=timezone.utc).astimezone(
                OPERATIONAL_TIMEZONE
            )
        if isinstance(value, str):
            normalized = value.strip().replace("Z", "+00:00")
            parsed = datetime.fromisoformat(normalized)
            if parsed.tzinfo is None:
                raise ValueError("timezone missing")
            return parsed.astimezone(OPERATIONAL_TIMEZONE)
    except (OverflowError, OSError, ValueError) as error:
        raise AttendanceError("A API retornou um horário do servidor inválido.") from error
    raise AttendanceError("A API retornou um horário do servidor inválido.")


def _parse_punch_timestamp(value: Any) -> datetime:
    try:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            epoch_seconds = value / 1000 if abs(value) >= 100_000_000_000 else value
            return datetime.fromtimestamp(epoch_seconds, tz=timezone.utc).astimezone(
                OPERATIONAL_TIMEZONE
            )
        if isinstance(value, str):
            normalized = value.strip().replace("Z", "+00:00")
            parsed = datetime.fromisoformat(normalized)
            if parsed.tzinfo is None:
                raise ValueError("timezone missing")
            return parsed.astimezone(OPERATIONAL_TIMEZONE)
    except (OverflowError, OSError, ValueError) as error:
        raise AttendanceError("A API retornou o horário de uma batida inválido.") from error
    raise AttendanceError("A API retornou o horário de uma batida inválido.")


def _parse_minute(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value < 1440:
        raise AttendanceError(f"A API retornou um horário inválido para {field}.")
    return value


def _parse_day_schedule(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise AttendanceError(
            "A API retornou uma jornada diária inválida "
            f"(tipo recebido: {type(value).__name__})."
        )
    is_workday_value = value.get("is_workday")
    if is_workday_value is True or is_workday_value == "true":
        is_workday = True
    elif is_workday_value is False or is_workday_value == "false":
        is_workday = False
    else:
        received_keys = sorted(
            key
            for key in value
            if isinstance(key, str) and key.isidentifier()
        )
        present_fields = ", ".join(received_keys[:12]) or "nenhuma"
        if len(received_keys) > 12:
            present_fields = f"{present_fields}, ..."
        detail = (
            "campo is_workday ausente"
            if "is_workday" not in value
            else f"is_workday com tipo {type(is_workday_value).__name__}"
        )
        raise AttendanceError(
            "A API retornou uma jornada diária inválida "
            f"({detail}; chaves recebidas: {present_fields})."
        )
    if not is_workday:
        if any(
            value.get(field) is not None
            for field in (
                "start_minute",
                "end_minute",
                "break_start_minute",
                "break_end_minute",
            )
        ):
            raise AttendanceError("A API retornou horários para um dia de folga.")
        return {"is_workday": False}

    start = _parse_minute(value.get("start_minute"), "entrada")
    end = _parse_minute(value.get("end_minute"), "saída")
    break_start_value = value.get("break_start_minute")
    break_end_value = value.get("break_end_minute")
    if end <= start:
        raise AttendanceError("A API retornou uma jornada diária fora de ordem.")
    if (break_start_value is None) != (break_end_value is None):
        raise AttendanceError("A API retornou um intervalo incompleto.")

    schedule = {
        "is_workday": True,
        "start_minute": start,
        "end_minute": end,
        "break_start_minute": None,
        "break_end_minute": None,
    }
    if break_start_value is not None:
        break_start = _parse_minute(break_start_value, "início do intervalo")
        break_end = _parse_minute(break_end_value, "fim do intervalo")
        if not start < break_start < break_end < end:
            raise AttendanceError("A API retornou um intervalo fora de ordem.")
        schedule["break_start_minute"] = break_start
        schedule["break_end_minute"] = break_end
    return schedule


def _parse_punches(value: Any, work_date: date) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise AttendanceError("A API retornou uma lista de batidas inválida.")
    punches: list[dict[str, str]] = []
    for record in value:
        if not isinstance(record, dict):
            raise AttendanceError("A API retornou uma batida inválida.")
        punch_type = record.get("punch_type")
        if not isinstance(punch_type, str) or punch_type not in PUNCH_LABELS:
            raise AttendanceError("A API retornou um tipo de batida inválido.")
        punched_at = _parse_punch_timestamp(
            record.get("punched_at", record.get("created_at"))
        )
        if punched_at.date() != work_date:
            raise AttendanceError("A API retornou uma batida de outra data.")
        punches.append(
            {
                "type": punch_type,
                "label": PUNCH_LABELS[punch_type],
                "at": punched_at.strftime("%H:%M"),
                "timestamp": punched_at.isoformat(),
            }
        )
    punches.sort(key=lambda punch: punch["timestamp"])
    return punches


def _expected_sequence(
    schedule: dict[str, Any],
) -> list[tuple[str, int]]:
    sequence = [("entry", schedule["start_minute"])]
    if schedule["break_start_minute"] is not None:
        sequence.extend(
            [
                ("break_start", schedule["break_start_minute"]),
                ("break_end", schedule["break_end_minute"]),
            ]
        )
    sequence.append(("exit", schedule["end_minute"]))
    return sequence


def _build_day(
    employee: dict[str, Any],
    schedule_value: Any,
    punches_value: Any,
    server_time: datetime,
    work_date: date,
) -> AttendanceDay:
    employee_id = _parse_id(employee.get("id"), "colaborador")
    employee_name = employee.get("employee_name", employee.get("name"))
    if not isinstance(employee_name, str) or not employee_name.strip():
        employee_name = "Não informado"
    job_title = employee.get("job_title")
    department = employee.get("department")
    status = employee.get("status")
    if not isinstance(status, str) or not status.strip():
        raise AttendanceError("A API retornou uma situação inválida para o colaborador.")
    schedule = _parse_day_schedule(schedule_value)
    punches = _parse_punches(punches_value, work_date)

    if schedule is None:
        state = "Jornada não cadastrada"
        schedule_summary = "Jornada não cadastrada"
        sequence: list[tuple[str, int]] = []
    elif not schedule["is_workday"]:
        state = "Folga"
        schedule_summary = "Folga"
        sequence = []
        if punches:
            raise AttendanceError("A API retornou batidas em um dia de folga.")
    else:
        sequence = _expected_sequence(schedule)
        schedule_summary = "; ".join(
            f"{PUNCH_LABELS[punch_type]} "
            f"{time(minute // 60, minute % 60).strftime('%H:%M')}"
            for punch_type, minute in sequence
        )
        recorded_types = [punch["type"] for punch in punches]
        expected_types = [item[0] for item in sequence]
        if recorded_types != expected_types[: len(recorded_types)]:
            raise AttendanceError("A API retornou batidas duplicadas ou fora de ordem.")
        if len(recorded_types) > len(expected_types):
            raise AttendanceError("A API retornou mais batidas que a jornada permite.")

        current_minute = server_time.hour * 60 + server_time.minute
        next_index = len(recorded_types)
        if next_index == len(sequence):
            state = "Concluído"
        elif next_index == 0:
            state = (
                "Aguardando horário"
                if current_minute < sequence[0][1]
                else "Não iniciou"
            )
        elif current_minute < sequence[next_index][1]:
            state = "Ponto aberto"
        else:
            state = "Incompleto"

    next_index = len(punches)
    if sequence and next_index < len(sequence):
        next_type, next_minute = sequence[next_index]
        next_label = PUNCH_LABELS[next_type]
        next_at = time(next_minute // 60, next_minute % 60).strftime("%H:%M")
        can_punch = (
            server_time.hour * 60 + server_time.minute >= next_minute
        )
    else:
        next_type = ""
        next_label = ""
        next_at = ""
        can_punch = False

    return AttendanceDay(
        employee_id=employee_id,
        employee_name=employee_name.strip(),
        job_title=job_title.strip() if isinstance(job_title, str) else "",
        department=department.strip() if isinstance(department, str) else "",
        status=status.strip(),
        state=state,
        schedule_summary=schedule_summary,
        next_punch=next_type,
        next_punch_label=next_label,
        next_punch_at=next_at,
        can_punch=can_punch,
        punches=punches,
    )


def _parse_work_date(value: Any) -> date:
    if not isinstance(value, str):
        raise AttendanceError("A API retornou uma data operacional inválida.")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise AttendanceError(
            "A API retornou uma data operacional inválida."
        ) from error
    return parsed


def _schedule_for_date(weekly_schedule: Any, work_date: date) -> Any:
    if weekly_schedule is None:
        return None
    if not isinstance(weekly_schedule, dict):
        raise AttendanceError("A API retornou uma jornada semanal inválida.")
    return weekly_schedule.get(WEEKDAYS[work_date.weekday()])


def _event_snapshot(punches: list[dict[str, Any]]) -> Any:
    for punch in punches:
        if isinstance(punch, dict) and punch.get("punch_type") == "entry":
            snapshot = punch.get("schedule_snapshot")
            if snapshot is not None:
                return snapshot
    return None


def _parse_my_attendance(data: Any) -> AttendanceDay:
    if not isinstance(data, dict):
        raise AttendanceError("A API retornou um registro diário inválido.")
    work_date = _parse_work_date(data.get("work_date"))
    server_time = _parse_server_time(data.get("server_now"))
    if server_time.date() != work_date:
        raise AttendanceError("A data do servidor diverge da data operacional.")
    employee = data.get("employee")
    if not isinstance(employee, dict):
        raise AttendanceError("A API não retornou o colaborador autenticado.")
    punches_value = data.get("punches")
    if not isinstance(punches_value, list):
        raise AttendanceError("A API retornou uma lista de batidas inválida.")
    schedule_value = _event_snapshot(punches_value)
    if schedule_value is None:
        schedule_value = data.get("schedule")
    if isinstance(schedule_value, dict) and all(
        day in schedule_value for day in WEEKDAYS
    ):
        schedule_value = _schedule_for_date(schedule_value, work_date)
    return _build_day(employee, schedule_value, punches_value, server_time, work_date)


def _parse_dashboard(data: Any) -> list[AttendanceDay]:
    if not isinstance(data, dict):
        raise AttendanceError("A API retornou um painel diário inválido.")
    work_date = _parse_work_date(data.get("work_date"))
    server_time = _parse_server_time(data.get("server_now"))
    if server_time.date() != work_date:
        raise AttendanceError("A data do servidor diverge da data operacional.")
    employees = data.get("employees")
    punches = data.get("punches")
    if not isinstance(employees, list) or not isinstance(punches, list):
        raise AttendanceError("A API retornou dados incompletos para o painel.")

    punches_by_employee: dict[str, list[dict[str, Any]]] = {}
    for punch in punches:
        if not isinstance(punch, dict):
            raise AttendanceError("A API retornou uma batida inválida.")
        employee_id = _parse_id(punch.get("employees_id"), "colaborador")
        punches_by_employee.setdefault(employee_id, []).append(punch)

    rows: list[AttendanceDay] = []
    seen_employee_ids: set[str] = set()
    for employee in employees:
        if not isinstance(employee, dict):
            raise AttendanceError("A API retornou um colaborador inválido.")
        employee_id = _parse_id(employee.get("id"), "colaborador")
        if employee_id in seen_employee_ids:
            raise AttendanceError("A API retornou colaboradores duplicados.")
        seen_employee_ids.add(employee_id)
        employee_punches = punches_by_employee.pop(employee_id, [])
        schedule_value = _event_snapshot(employee_punches)
        if schedule_value is None:
            schedule_value = _schedule_for_date(
                employee.get("weekly_schedule"), work_date
            )
        rows.append(
            _build_day(
                employee,
                schedule_value,
                employee_punches,
                server_time,
                work_date,
            )
        )
    if punches_by_employee:
        raise AttendanceError("A API retornou batidas sem colaborador ativo.")
    return rows


async def get_my_attendance(api_url: str, token: str) -> AttendanceDay:
    """Consulta o ponto diário do colaborador identificado pelo token."""
    normalized_url = _validate_api_url(api_url)
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.get(
            f"{normalized_url}/attendance/me",
            headers=_authorization_headers(token),
        )
    return _parse_my_attendance(
        _parse_response(response, "consultar o próprio ponto")
    )


async def record_next_punch(api_url: str, token: str) -> AttendanceDay:
    """Solicita a próxima batida; tipo, data e horário são definidos no Xano."""
    normalized_url = _validate_api_url(api_url)
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.post(
            f"{normalized_url}/attendance/me/punch",
            headers=_authorization_headers(token),
            json={},
        )
    return _parse_my_attendance(
        _parse_response(response, "registrar a próxima batida")
    )


async def get_daily_attendance(api_url: str, token: str) -> list[AttendanceDay]:
    """Consulta o acompanhamento diário autorizado do Gestor RH."""
    normalized_url = _validate_api_url(api_url)
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.get(
            f"{normalized_url}/attendance/today",
            headers=_authorization_headers(token),
        )
    return _parse_dashboard(
        _parse_response(response, "consultar o painel diário de ponto")
    )
