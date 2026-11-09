"""Serviço de gestão de solicitações de férias no Xano."""

from dataclasses import dataclass
from datetime import date
from typing import Any

import httpx

REQUEST_TIMEOUT_SECONDS = 12
VACATION_STATUSES = {"Pendente", "Aprovada", "Rejeitada"}
DECISION_STATUSES = {"Aprovada", "Rejeitada"}


class VacationRequestError(Exception):
    """Erro ao consultar ou alterar solicitações de férias."""


class VacationAccessDenied(VacationRequestError):
    """O Xano recusou a operação por falta de permissão."""


@dataclass(frozen=True)
class VacationRequest:
    id: str
    employee_id: str
    employee_name: str
    start_date: str
    end_date: str
    status: str

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "employee_name": self.employee_name,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "status": self.status,
        }


def _validate_api_url(api_url: str) -> str:
    normalized_url = api_url.rstrip("/")
    if not normalized_url:
        raise VacationRequestError(
            "Configure a variável XANO_RH_API_URL para conectar à API de RH."
        )
    return normalized_url


def _authorization_headers(token: str) -> dict[str, str]:
    if not token:
        raise VacationAccessDenied("Sessão inválida. Entre novamente.")
    return {"Authorization": f"Bearer {token}"}


def _raise_for_response(response: httpx.Response, operation: str) -> None:
    if response.status_code in (401, 403):
        raise VacationAccessDenied(
            "Seu perfil não tem autorização para gerenciar férias."
        )
    if response.is_error:
        raise VacationRequestError(
            f"Não foi possível {operation} no Xano (HTTP {response.status_code})."
        )


def _parse_id(value: Any, field: str) -> str:
    if (
        not isinstance(value, (str, int))
        or isinstance(value, bool)
        or not str(value).strip()
    ):
        raise VacationRequestError(
            f"A API retornou um identificador inválido para {field}."
        )
    try:
        parsed_id = int(value)
    except ValueError as error:
        raise VacationRequestError(
            f"A API retornou um identificador inválido para {field}."
        ) from error
    if parsed_id < 1:
        raise VacationRequestError(
            f"A API retornou um identificador inválido para {field}."
        )
    return str(parsed_id)


def _parse_date(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise VacationRequestError(
            f"A API retornou uma data inválida para {field}."
        )
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as error:
        raise VacationRequestError(
            f"A API retornou uma data inválida para {field}."
        ) from error


def _parse_vacation_request(record: Any) -> VacationRequest:
    if not isinstance(record, dict):
        raise VacationRequestError(
            "A API retornou uma solicitação de férias inválida."
        )
    status = record.get("status")
    if not isinstance(status, str) or status not in VACATION_STATUSES:
        raise VacationRequestError(
            "A API retornou uma situação inválida para férias."
        )
    employee_name = record.get("employee_name")
    if not isinstance(employee_name, str) or not employee_name.strip():
        employee_name = "Não informado"
    start_date = _parse_date(record.get("start_date"), "início")
    end_date = _parse_date(record.get("end_date"), "fim")
    if start_date > end_date:
        raise VacationRequestError(
            "A API retornou um período de férias inválido."
        )

    return VacationRequest(
        id=_parse_id(record.get("id"), "solicitação"),
        employee_id=_parse_id(record.get("employees_id"), "colaborador"),
        employee_name=employee_name.strip(),
        start_date=start_date,
        end_date=end_date,
        status=status,
    )


def _parse_response(response: httpx.Response, operation: str) -> Any:
    _raise_for_response(response, operation)
    try:
        return response.json()
    except ValueError as error:
        raise VacationRequestError(
            "A API retornou uma resposta inválida para férias."
        ) from error


async def list_vacation_requests(
    api_url: str, token: str
) -> list[VacationRequest]:
    """Lista solicitações de férias confirmadas pelo Xano."""
    normalized_url = _validate_api_url(api_url)
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.get(
            f"{normalized_url}/vacation_requests",
            headers=_authorization_headers(token),
        )
    data = _parse_response(response, "consultar solicitações de férias")
    if not isinstance(data, list):
        raise VacationRequestError(
            "A API retornou um formato inválido para solicitações de férias."
        )
    return [_parse_vacation_request(record) for record in data]


async def create_vacation_request(
    api_url: str,
    token: str,
    employee_id: str,
    start_date: str,
    end_date: str,
) -> str:
    """Cria uma solicitação pendente em nome de um funcionário."""
    normalized_url = _validate_api_url(api_url)
    parsed_employee_id = _parse_id(employee_id, "colaborador")
    normalized_start_date = _parse_date(start_date, "início")
    normalized_end_date = _parse_date(end_date, "fim")
    if normalized_start_date > normalized_end_date:
        raise VacationRequestError(
            "A data de início não pode ser posterior à data de fim."
        )

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.post(
            f"{normalized_url}/vacation_requests",
            headers=_authorization_headers(token),
            json={
                "employees_id": int(parsed_employee_id),
                "start_date": normalized_start_date,
                "end_date": normalized_end_date,
            },
        )
    data = _parse_response(response, "cadastrar a solicitação de férias")
    if not isinstance(data, dict):
        raise VacationRequestError(
            "A API não confirmou a solicitação de férias."
        )
    return _parse_id(data.get("id"), "solicitação")


async def decide_vacation_request(
    api_url: str, token: str, request_id: str, status: str
) -> None:
    """Aprova ou rejeita uma solicitação ainda pendente."""
    normalized_url = _validate_api_url(api_url)
    parsed_request_id = _parse_id(request_id, "solicitação")
    if status not in DECISION_STATUSES:
        raise VacationRequestError("Selecione uma decisão válida.")

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.patch(
            f"{normalized_url}/vacation_requests/{parsed_request_id}",
            headers=_authorization_headers(token),
            json={"status": status},
        )
    data = _parse_response(response, "decidir a solicitação de férias")
    if not isinstance(data, dict) or data.get("status") != status:
        raise VacationRequestError(
            "A API não confirmou a decisão da solicitação de férias."
        )


def count_current_vacation_employees(
    requests: list[VacationRequest], today: date | None = None
) -> int:
    """Conta funcionários distintos com férias aprovadas na data informada."""
    current_date = today or date.today()
    employee_ids = {
        request.employee_id
        for request in requests
        if request.status == "Aprovada"
        and request.start_date <= current_date.isoformat()
        and request.end_date >= current_date.isoformat()
    }
    return len(employee_ids)
