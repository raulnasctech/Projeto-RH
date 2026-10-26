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


async def list_departments(api_url: str, token: str) -> list[dict[str, Any]]:
    normalized_url = _validate_api_url(api_url)
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.get(
            f"{normalized_url}/departments",
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code in (401, 403):
        raise DepartmentAccessDenied(f"Sem autorização para listar departamentos: {response.text}")
    if response.is_error:
        raise DepartmentError(f"Erro Xano ({response.status_code}): {response.text}")

    try:
        data = response.json()
    except ValueError as error:
        raise DepartmentError("Resposta inválida da API.") from error

    if not isinstance(data, list):
        return []
    return data


async def create_department(api_url: str, token: str, name: str) -> int:
    normalized_url = _validate_api_url(api_url)
    norm_name = name.strip()
    if not norm_name:
        raise DepartmentError("O nome do departamento não pode estar vazio.")

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.post(
            f"{normalized_url}/departments",
            headers={"Authorization": f"Bearer {token}"},
            json={"nome": norm_name},
        )

    if response.status_code in (401, 403):
        raise DepartmentAccessDenied(f"Sem autorização para criar departamento: {response.text}")
    if response.is_error:
        raise DepartmentError(f"Erro Xano ({response.status_code}): {response.text}")

    try:
        data = response.json()
    except ValueError as error:
        raise DepartmentError("Resposta inválida da API.") from error

    return int(data.get("id", 0))


async def update_department(api_url: str, token: str, dept_id: str, name: str) -> None:
    normalized_url = _validate_api_url(api_url)
    norm_name = name.strip()
    if not norm_name:
        raise DepartmentError("O nome do departamento não pode estar vazio.")

    try:
        parsed_id = int(dept_id)
    except (TypeError, ValueError) as error:
        raise DepartmentError("ID de departamento inválido.") from error

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.patch(
            f"{normalized_url}/departments/{parsed_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"nome": norm_name},
        )

    if response.status_code in (401, 403):
        raise DepartmentAccessDenied(f"Sem autorização para atualizar departamento: {response.text}")
    if response.is_error:
        raise DepartmentError(f"Erro Xano ({response.status_code}): {response.text}")
