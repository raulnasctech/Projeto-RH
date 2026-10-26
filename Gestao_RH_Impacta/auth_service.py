"""Serviços de autenticação e consulta de identidade no Xano."""

from dataclasses import dataclass
from typing import Any

import httpx


REQUEST_TIMEOUT_SECONDS = 12
GENERIC_AUTH_ERROR = "Não foi possível concluir a autenticação."


class AuthenticationError(Exception):
    """Erro de autenticação que pode ser apresentado sem expor credenciais."""


class SessionRejected(AuthenticationError):
    """O Xano rejeitou ou expirou o token da sessão."""


@dataclass(frozen=True)
class AuthenticatedUser:
    token: str
    user_name: str


def _response_data(response: httpx.Response) -> dict[str, Any]:
    try:
        data = response.json()
    except ValueError as error:
        raise AuthenticationError(GENERIC_AUTH_ERROR) from error
    if not isinstance(data, dict):
        raise AuthenticationError(GENERIC_AUTH_ERROR)
    return data


def _error_message(response: httpx.Response) -> str:
    try:
        data = response.json()
    except ValueError:
        return GENERIC_AUTH_ERROR
    if isinstance(data, dict):
        message = data.get("message") or data.get("error")
        if isinstance(message, str) and message.strip():
            return message
    return GENERIC_AUTH_ERROR


async def _get_identity(
    client: httpx.AsyncClient,
    api_url: str,
    token: str,
    expected_user_id: str | int | None = None,
) -> str:
    response = await client.get(
        f"{api_url}/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    if response.status_code in (401, 403):
        raise SessionRejected("Sua sessão expirou. Entre novamente.")
    if response.is_error:
        raise AuthenticationError(_error_message(response))

    profile = _response_data(response)
    user_id = profile.get("id")
    if (
        not isinstance(user_id, (str, int))
        or isinstance(user_id, bool)
        or not str(user_id).strip()
        or (
            expected_user_id is not None
            and str(user_id) != str(expected_user_id)
        )
    ):
        raise AuthenticationError(GENERIC_AUTH_ERROR)

    name = profile.get("name")
    return name if isinstance(name, str) else ""


async def authenticate(
    api_url: str,
    endpoint: str,
    payload: dict[str, str],
) -> AuthenticatedUser:
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.post(f"{api_url}{endpoint}", json=payload)
        if response.is_error:
            raise AuthenticationError(_error_message(response))

        data = _response_data(response)
        token = data.get("authToken")
        user_id = data.get("user_id")
        if (
            not isinstance(token, str)
            or not token
            or not isinstance(user_id, (str, int))
            or isinstance(user_id, bool)
            or not str(user_id).strip()
        ):
            raise AuthenticationError(GENERIC_AUTH_ERROR)

        user_name = await _get_identity(client, api_url, token, user_id)
        return AuthenticatedUser(token=token, user_name=user_name)


async def get_authenticated_user(api_url: str, token: str) -> AuthenticatedUser:
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        user_name = await _get_identity(client, api_url, token)
    return AuthenticatedUser(token=token, user_name=user_name)
