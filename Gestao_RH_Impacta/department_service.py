"""Serviço de gestão de departamentos no Xano."""

from typing import Any

import httpx

REQUEST_TIMEOUT_SECONDS = 15.0


class DepartmentError(Exception):
    pass


class DepartmentAccessDenied(Exception):
    pass


def _validate_api_url(api_url: str) -> str:
    if not api_url:
        raise DepartmentError("URL da API de RH não configurada.")
    return api_url.rstrip("/")


def _authorization_headers(token: str) -> dict[str, str]:
    if not token:
        raise DepartmentAccessDenied("Sessão inválida. Entre novamente.")
    return {"Authorization": f"Bearer {token}"}


def _parse_department_id(data: dict[str, Any]) -> int:
    department_id = data.get("id")
    if (
        not isinstance(department_id, (int, str))
        or isinstance(department_id, bool)
        or not str(department_id).strip()
    ):
        raise DepartmentError(
            "A API retornou um departamento sem identificador válido."
        )
    try:
        parsed_id = int(department_id)
    except ValueError as error:
        raise DepartmentError(
            "A API retornou um departamento sem identificador válido."
        ) from error
    if parsed_id < 1:
        raise DepartmentError(
            "A API retornou um departamento sem identificador válido."
        )
    return parsed_id


async def list_departments(api_url: str, token: str) -> list[dict[str, str]]:
    normalized_url = _validate_api_url(api_url)
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.get(
            f"{normalized_url}/departments",
            headers=_authorization_headers(token),
        )

    if response.status_code in (401, 403):
        raise DepartmentAccessDenied(
            f"Sem autorização para listar departamentos (HTTP {response.status_code})."
        )
    if response.is_error:
        raise DepartmentError(
            f"Erro Xano ao listar departamentos (HTTP {response.status_code})."
        )

    try:
        data = response.json()
    except ValueError as error:
        raise DepartmentError("Resposta inválida da API.") from error

    if not isinstance(data, list):
        raise DepartmentError("A API retornou um formato inválido para departamentos.")

    departments = []
    for record in data:
        if not isinstance(record, dict):
            raise DepartmentError("A API retornou um departamento inválido.")
        name = record.get("name", record.get("nome"))
        if not isinstance(name, str) or not name.strip():
            raise DepartmentError("A API retornou um departamento sem nome válido.")
        departments.append(
            {"id": str(_parse_department_id(record)), "name": name.strip()}
        )
    return departments


async def create_department(api_url: str, token: str, name: str) -> int:
    normalized_url = _validate_api_url(api_url)
    norm_name = name.strip()
    if not norm_name:
        raise DepartmentError("O nome do departamento não pode estar vazio.")

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.post(
            f"{normalized_url}/departments",
            headers=_authorization_headers(token),
            json={"nome": norm_name},
        )

    if response.status_code in (401, 403):
        raise DepartmentAccessDenied(
            f"Sem autorização para criar departamento (HTTP {response.status_code})."
        )
    if response.is_error:
        raise DepartmentError(
            f"Erro Xano ao cadastrar departamento (HTTP {response.status_code})."
        )

    try:
        data = response.json()
    except ValueError as error:
        raise DepartmentError("Resposta inválida da API.") from error

    if not isinstance(data, dict):
        raise DepartmentError("A API retornou um departamento inválido.")
    return _parse_department_id(data)


async def update_department(
    api_url: str, token: str, dept_id: str, name: str
) -> None:
    normalized_url = _validate_api_url(api_url)
    norm_name = name.strip()
    if not norm_name:
        raise DepartmentError("O nome do departamento não pode estar vazio.")

    try:
        parsed_id = int(dept_id)
    except (TypeError, ValueError) as error:
        raise DepartmentError("ID de departamento inválido.") from error
    if parsed_id < 1:
        raise DepartmentError("ID de departamento inválido.")

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.patch(
            f"{normalized_url}/departments/{parsed_id}",
            headers=_authorization_headers(token),
            json={"nome": norm_name},
        )

    if response.status_code in (401, 403):
        raise DepartmentAccessDenied(
            f"Sem autorização para atualizar departamento (HTTP {response.status_code})."
        )
    if response.is_error:
        raise DepartmentError(
            f"Erro Xano ao atualizar departamento (HTTP {response.status_code})."
        )
