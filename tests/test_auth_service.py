import json
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

from Gestao_RH_Impacta import auth_service
from Gestao_RH_Impacta import Gestao_RH_Impacta as app_module


FIXTURES = json.loads(
    (Path(__file__).parent / "fixtures" / "authentication.json").read_text(
        encoding="utf-8"
    )
)


class FakeAsyncClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False

    async def post(self, url, **kwargs):
        self.calls.append(("POST", url, kwargs))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    async def get(self, url, **kwargs):
        self.calls.append(("GET", url, kwargs))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def response(fixture_name):
    fixture = FIXTURES[fixture_name]
    return httpx.Response(fixture["status"], json=fixture["body"])


class AuthenticationServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_login_uses_xano_contract_and_confirms_identity(self):
        client = FakeAsyncClient(
            [response("login_success"), response("identity_success")]
        )
        with patch.object(auth_service.httpx, "AsyncClient", return_value=client):
            user = await auth_service.authenticate(
                "https://example.xano.io/api:auth",
                "/auth/login",
                {"email": "teste@example.com", "password": "senha-teste"},
            )

        self.assertEqual(user.token, "fixture-login-token")
        self.assertEqual(user.user_name, "Usuário de teste")
        self.assertEqual(client.calls[0][0], "POST")
        self.assertEqual(client.calls[1][0], "GET")
        self.assertEqual(
            client.calls[1][2]["headers"]["Authorization"],
            "Bearer fixture-login-token",
        )

    async def test_signup_uses_the_same_identity_confirmation(self):
        client = FakeAsyncClient(
            [response("signup_success"), response("identity_signup_success")]
        )
        with patch.object(auth_service.httpx, "AsyncClient", return_value=client):
            user = await auth_service.authenticate(
                "https://example.xano.io/api:auth",
                "/auth/signup",
                {
                    "name": "Novo usuário",
                    "email": "novo@example.com",
                    "password": "senha-teste",
                    "cpf": "",
                    "celular": "",
                },
            )

        self.assertEqual(user.token, "fixture-signup-token")
        self.assertEqual(user.user_name, "Novo usuário")

    async def test_rejected_credentials_do_not_create_a_session(self):
        client = FakeAsyncClient([response("login_rejected")])
        with patch.object(auth_service.httpx, "AsyncClient", return_value=client):
            with self.assertRaisesRegex(
                auth_service.AuthenticationError, "Invalid Credentials"
            ):
                await auth_service.authenticate(
                    "https://example.xano.io/api:auth",
                    "/auth/login",
                    {"email": "teste@example.com", "password": "errada"},
                )

        self.assertEqual(len(client.calls), 1)

    async def test_missing_or_mismatched_identity_is_rejected(self):
        login = response("login_success")
        identity = httpx.Response(200, json={"id": 99, "name": "Outra pessoa"})
        client = FakeAsyncClient([login, identity])
        with patch.object(auth_service.httpx, "AsyncClient", return_value=client):
            with self.assertRaises(auth_service.AuthenticationError):
                await auth_service.authenticate(
                    "https://example.xano.io/api:auth",
                    "/auth/login",
                    {"email": "teste@example.com", "password": "senha-teste"},
                )

        client = FakeAsyncClient(
            [response("login_success"), httpx.Response(200, json={"name": "Sem ID"})]
        )
        with patch.object(auth_service.httpx, "AsyncClient", return_value=client):
            with self.assertRaises(auth_service.AuthenticationError):
                await auth_service.authenticate(
                    "https://example.xano.io/api:auth",
                    "/auth/login",
                    {"email": "teste@example.com", "password": "senha-teste"},
                )

    async def test_incomplete_authentication_response_is_rejected(self):
        client = FakeAsyncClient([httpx.Response(200, json={"user_id": 17})])
        with patch.object(auth_service.httpx, "AsyncClient", return_value=client):
            with self.assertRaises(auth_service.AuthenticationError):
                await auth_service.authenticate(
                    "https://example.xano.io/api:auth",
                    "/auth/login",
                    {"email": "teste@example.com", "password": "senha-teste"},
                )

    async def test_expired_token_is_reported_as_rejected_session(self):
        client = FakeAsyncClient([response("identity_rejected")])
        with patch.object(auth_service.httpx, "AsyncClient", return_value=client):
            with self.assertRaises(auth_service.SessionRejected):
                await auth_service.get_authenticated_user(
                    "https://example.xano.io/api:auth", "fixture-token"
                )

    async def test_token_is_not_in_client_state_delta(self):
        state = app_module.State(_reflex_internal_init=True)
        state._auth_token = "do-not-expose-token"
        state._auth_user_name = "Usuário de teste"
        state._password = "do-not-expose-password"

        delta = str(state.get_delta())

        self.assertNotIn("do-not-expose-token", delta)
        self.assertNotIn("do-not-expose-password", delta)
        self.assertNotIn("_auth_token", delta)
        self.assertNotIn("_password", delta)
        self.assertIn("Usuário de teste", delta)

    async def test_authentication_does_not_log_credentials_or_token(self):
        client = FakeAsyncClient(
            [response("login_success"), response("identity_success")]
        )
        with patch.object(auth_service.httpx, "AsyncClient", return_value=client):
            with self.assertNoLogs(level="DEBUG"):
                await auth_service.authenticate(
                    "https://example.xano.io/api:auth",
                    "/auth/login",
                    {"email": "teste@example.com", "password": "password-secret"},
                )

    async def test_login_failure_does_not_leave_password_in_state(self):
        state = app_module.State(_reflex_internal_init=True)
        state._password = "senha-teste"
        with patch.object(
            app_module,
            "authenticate",
            side_effect=auth_service.AuthenticationError("Acesso negado."),
        ):
            self.assertFalse(
                await state._authenticate(
                    "/auth/login",
                    {"email": "teste@example.com", "password": "senha-teste"},
                )
            )

        self.assertFalse(state.is_authenticated)
        self.assertEqual(state._password, "")
        self.assertNotIn("senha-teste", str(state.get_delta()))

    async def test_login_failure_returns_browser_password_clear_event(self):
        state = app_module.State(_reflex_internal_init=True)
        state.email = "teste@example.com"
        state._password = "senha-teste"
        with (
            patch.object(app_module, "XANO_AUTH_API_URL", "https://example.xano.io"),
            patch.object(
                app_module,
                "authenticate",
                side_effect=auth_service.AuthenticationError("Acesso negado."),
            ),
        ):
            event = await state.submit_login()

        self.assertIsNotNone(event)
        self.assertEqual(state._password, "")

    async def test_connection_failure_does_not_start_a_session(self):
        state = app_module.State(_reflex_internal_init=True)
        state._password = "senha-teste"
        client = FakeAsyncClient([httpx.ConnectError("connection failed")])
        with patch.object(auth_service.httpx, "AsyncClient", return_value=client):
            self.assertFalse(
                await state._authenticate(
                    "/auth/login",
                    {"email": "teste@example.com", "password": "senha-teste"},
                )
            )

        self.assertFalse(state.is_authenticated)
        self.assertEqual(state._auth_token, "")
        self.assertEqual(state._password, "")

    async def test_authenticated_states_do_not_share_tokens(self):
        first = app_module.State(_reflex_internal_init=True)
        second = app_module.State(_reflex_internal_init=True)
        first._auth_token = "first-session-token"
        first._authenticated = True

        self.assertEqual(first._auth_token, "first-session-token")
        self.assertEqual(second._auth_token, "")
        self.assertTrue(first.is_authenticated)
        self.assertFalse(second.is_authenticated)

    async def test_successful_authentication_starts_server_session(self):
        state = app_module.State(_reflex_internal_init=True)
        with patch.object(
            app_module,
            "authenticate",
            return_value=auth_service.AuthenticatedUser(
                token="fixture-token", user_name="Usuário de teste"
            ),
        ):
            self.assertTrue(
                await state._authenticate(
                    "/auth/login",
                    {"email": "teste@example.com", "password": "senha-teste"},
                )
            )

        self.assertEqual(state._auth_token, "fixture-token")
        self.assertEqual(state.user_name, "Usuário de teste")
        self.assertTrue(state.is_authenticated)
        self.assertTrue(state._skip_next_auth_check)
        self.assertEqual(state._password, "")

    async def test_first_page_load_skips_duplicate_identity_request_after_login(self):
        state = app_module.State(_reflex_internal_init=True)
        state._auth_token = "fixture-token"
        state._authenticated = True
        state._skip_next_auth_check = True

        with patch.object(app_module, "get_authenticated_user") as get_user:
            redirect = await state.require_auth()

        self.assertIsNone(redirect)
        self.assertFalse(state._skip_next_auth_check)
        get_user.assert_not_called()

        with patch.object(
            app_module,
            "get_authenticated_user",
            return_value=auth_service.AuthenticatedUser(
                token="fixture-token", user_name="Usuário de teste"
            ),
        ) as get_user:
            redirect = await state.require_auth()

        self.assertIsNone(redirect)
        get_user.assert_awaited_once()

    async def test_logout_clears_session(self):
        state = app_module.State(_reflex_internal_init=True)
        state._auth_token = "fixture-token"
        state._auth_user_name = "Usuário de teste"
        state._authenticated = True
        state._password = "senha-teste"

        state.sign_out()

        self.assertEqual(state._auth_token, "")
        self.assertEqual(state.user_name, "")
        self.assertFalse(state.is_authenticated)
        self.assertFalse(state._skip_next_auth_check)
        self.assertEqual(state._password, "")

    async def test_expired_session_clears_token_and_redirects(self):
        state = app_module.State(_reflex_internal_init=True)
        state._auth_token = "fixture-token"
        state._authenticated = True
        with patch.object(
            app_module,
            "get_authenticated_user",
            side_effect=auth_service.SessionRejected("Sessão expirada."),
        ):
            redirect = await state.require_auth()

        self.assertEqual(state._auth_token, "")
        self.assertFalse(state.is_authenticated)
        self.assertEqual(state.error_message, "Sua sessão expirou. Entre novamente.")
        self.assertIsNotNone(redirect)

    async def test_valid_session_is_confirmed_on_internal_navigation(self):
        state = app_module.State(_reflex_internal_init=True)
        state._auth_token = "fixture-token"
        with patch.object(
            app_module,
            "get_authenticated_user",
            return_value=auth_service.AuthenticatedUser(
                token="fixture-token", user_name="Usuário de teste"
            ),
        ):
            redirect = await state.require_auth()

        self.assertIsNone(redirect)
        self.assertTrue(state.is_authenticated)
        self.assertEqual(state.user_name, "Usuário de teste")

    async def test_missing_session_redirects_from_internal_navigation(self):
        state = app_module.State(_reflex_internal_init=True)

        redirect = await state.require_auth()

        self.assertIsNotNone(redirect)
        self.assertFalse(state.is_authenticated)

    async def test_every_internal_route_uses_auth_guard(self):
        pages = app_module.app._unevaluated_pages
        public_routes = {"index", "cadastro"}

        for route, page in pages.items():
            with self.subTest(route=route):
                if route in public_routes:
                    self.assertIsNone(page.on_load)
                else:
                    self.assertIsNotNone(page.on_load)
                    expected_handler = (
                        "load_employees"
                        if route in {"colaboradores", "inicio"}
                        else "load_departments"
                        if route == "departamentos"
                        else "require_auth"
                    )
                    self.assertEqual(page.on_load.fn.__name__, expected_handler)


if __name__ == "__main__":
    unittest.main()
