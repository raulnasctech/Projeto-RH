"""Tela de acesso do Sistema de Gestão de RH."""

import os

import httpx
import reflex as rx
from dotenv import load_dotenv


load_dotenv()
XANO_AUTH_API_URL = os.getenv("XANO_AUTH_API_URL", "").rstrip("/")


class State(rx.State):
    """Estado do formulário de acesso."""

    email: str = ""
    password: str = ""
    name: str = ""
    cpf: str = ""
    celular: str = ""
    show_password: bool = False
    error_message: str = ""
    auth_token: str = rx.LocalStorage(name="xano_auth_token")
    user_name: str = rx.LocalStorage(name="xano_user_name")

    def set_email(self, email: str):
        self.email = email

    def set_password(self, password: str):
        self.password = password

    def set_name(self, name: str):
        self.name = name

    def set_cpf(self, cpf: str):
        self.cpf = cpf

    def set_celular(self, celular: str):
        self.celular = celular

    def set_show_password(self, show_password: bool):
        self.show_password = show_password

    def _validate_credentials(self) -> bool:
        if not self.email.strip() or not self.password:
            self.error_message = "Informe seu e-mail e sua senha para continuar."
            return False
        elif "@" not in self.email:
            self.error_message = "Digite um endereço de e-mail válido."
            return False
        if not XANO_AUTH_API_URL:
            self.error_message = "Configure a variável XANO_AUTH_API_URL para conectar ao Xano."
            return False
        return True

    async def _authenticate(self, endpoint: str, payload: dict) -> bool:
        try:
            async with httpx.AsyncClient(timeout=12) as client:
                response = await client.post(f"{XANO_AUTH_API_URL}{endpoint}", json=payload)
            if response.is_error:
                detail = response.json().get("message") or response.json().get("error")
                self.error_message = detail or "Não foi possível concluir a solicitação."
                return False
            token = response.json().get("authToken")
            if not token:
                self.error_message = "O Xano não retornou um token de acesso."
                return False
            self.auth_token = token
            async with httpx.AsyncClient(timeout=12) as client:
                profile = await client.get(
                    f"{XANO_AUTH_API_URL}/auth/me",
                    headers={"Authorization": f"Bearer {token}"},
                )
            if profile.is_success:
                self.user_name = profile.json().get("name", "")
            self.password = ""
            self.error_message = ""
            return True
        except (httpx.HTTPError, ValueError):
            self.error_message = "Não foi possível conectar ao Xano. Verifique a URL da API."
            return False

    async def submit_login(self):
        """Autentica as credenciais no endpoint Xano e abre o painel."""
        if self._validate_credentials() and await self._authenticate(
            "/auth/login", {"email": self.email, "password": self.password}
        ):
            return rx.redirect("/inicio")

    async def submit_signup(self):
        """Cria o usuário no Xano e inicia sua sessão."""
        if not self.name.strip():
            self.error_message = "Informe seu nome para criar a conta."
            return
        if not self._validate_credentials():
            return
        if len(self.password) < 8:
            self.error_message = "A senha deve ter ao menos 8 caracteres."
            return
        if await self._authenticate(
            "/auth/signup",
            {
                "name": self.name,
                "email": self.email,
                "password": self.password,
                "cpf": self.cpf,
                "celular": self.celular,
            },
        ):
            return rx.redirect("/inicio")

    def sign_out(self):
        self.auth_token = ""
        self.user_name = ""
        self.password = ""
        return rx.redirect("/")


def brand(inverted: bool = False) -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.text("RH", color="white", weight="bold", font_size="1.05rem"),
            width="42px", height="42px", display="flex", align_items="center",
            justify_content="center", border_radius="13px",
            background="linear-gradient(135deg, #36c9a2 0%, #12866c 100%)",
            box_shadow="0 8px 22px rgba(20, 142, 113, 0.26)",
        ),
        rx.vstack(
            rx.text("IMPACTA", weight="bold", letter_spacing="0.12em", color="white" if inverted else "#163d36"),
            rx.text(
                "GESTÃO DE PESSOAS", font_size="0.62rem", letter_spacing="0.1em",
                color="#b7d2cb" if inverted else "#6c8580",
            ),
            spacing="0", align_items="start",
        ),
        spacing="3", align="center",
    )


def login_form() -> rx.Component:
    return rx.box(
        brand(),
        rx.vstack(
            rx.vstack(
                rx.heading("Boas-vindas!", size="7", color="#173b35", letter_spacing="-0.025em"),
                rx.text("Acesse sua conta para gerenciar sua jornada.", color="#68807b", font_size="0.98rem"),
                spacing="1", align_items="start",
            ),
            rx.vstack(
                rx.vstack(
                    rx.text("E-mail corporativo", weight="medium", color="#35534c", font_size="0.9rem"),
                    rx.input(
                        placeholder="nome@empresa.com", type="email", value=State.email,
                        on_change=State.set_email, width="100%", height="48px", border_radius="10px",
                        border="1px solid #d8e5e1", background="white", color="#173b35",
                    ),
                    spacing="2", width="100%",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.text("Senha", weight="medium", color="#35534c", font_size="0.9rem"),
                        rx.link("Esqueci minha senha", href="#", color="#16866d", font_size="0.84rem", weight="medium"),
                        justify="between", width="100%",
                    ),
                    rx.input(
                        placeholder="Digite sua senha", type=rx.cond(State.show_password, "text", "password"),
                        value=State.password, on_change=State.set_password, on_blur=State.submit_login,
                        width="100%", height="48px",
                        border_radius="10px", border="1px solid #d8e5e1", background="white", color="#173b35",
                    ),
                    rx.checkbox(
                        "Exibir senha", checked=State.show_password, on_change=State.set_show_password,
                        color="#52706a", font_size="0.84rem",
                    ),
                    spacing="2", width="100%",
                ),
                rx.cond(State.error_message != "", rx.text(State.error_message, color="#bd3e45", font_size="0.85rem")),
                rx.button(
                    "Entrar na plataforma", on_click=State.submit_login, width="100%", height="50px",
                    border_radius="10px", background="#15856d", color="white", font_weight="600",
                    _hover={"background": "#106f5b"},
                ),
                spacing="4", width="100%",
            ),
            rx.hstack(
                rx.text("Ainda não tem acesso?", color="#8aa09a", font_size="0.82rem"),
                rx.link("Criar conta", href="/cadastro", color="#16866d", font_size="0.82rem", weight="medium"),
                justify="center", width="100%", spacing="2",
            ),
            spacing="7", width="100%", margin_top="68px",
        ),
        width="100%", max_width="465px", padding="42px", background="rgba(255, 255, 255, 0.94)",
        border="1px solid rgba(220, 235, 229, 0.9)", border_radius="20px",
        box_shadow="0 24px 70px rgba(28, 74, 64, 0.12)",
    )


def signup_form() -> rx.Component:
    field_style = {
        "width": "100%", "height": "46px", "border_radius": "10px",
        "border": "1px solid #d8e5e1", "background": "white", "color": "#173b35",
    }
    return rx.box(
        brand(),
        rx.vstack(
            rx.vstack(
                rx.heading("Crie sua conta", size="7", color="#173b35", letter_spacing="-0.025em"),
                rx.text("Preencha seus dados para acessar a plataforma.", color="#68807b", font_size="0.95rem"),
                spacing="1", align_items="start",
            ),
            rx.vstack(
                rx.vstack(
                    rx.text("Nome completo", weight="medium", color="#35534c", font_size="0.88rem"),
                    rx.input(placeholder="Seu nome", value=State.name, on_change=State.set_name, **field_style),
                    spacing="2", width="100%",
                ),
                rx.vstack(
                    rx.text("E-mail", weight="medium", color="#35534c", font_size="0.88rem"),
                    rx.input(placeholder="nome@empresa.com", type="email", value=State.email, on_change=State.set_email, **field_style),
                    spacing="2", width="100%",
                ),
                rx.hstack(
                    rx.vstack(
                        rx.text("CPF", weight="medium", color="#35534c", font_size="0.88rem"),
                        rx.input(placeholder="Opcional", value=State.cpf, on_change=State.set_cpf, **field_style),
                        spacing="2", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Celular", weight="medium", color="#35534c", font_size="0.88rem"),
                        rx.input(placeholder="Opcional", value=State.celular, on_change=State.set_celular, **field_style),
                        spacing="2", width="100%",
                    ),
                    spacing="3", width="100%",
                ),
                rx.vstack(
                    rx.text("Senha", weight="medium", color="#35534c", font_size="0.88rem"),
                    rx.input(
                        placeholder="Mínimo de 8 caracteres", type=rx.cond(State.show_password, "text", "password"),
                        value=State.password, on_change=State.set_password, **field_style,
                    ),
                    rx.checkbox("Exibir senha", checked=State.show_password, on_change=State.set_show_password,
                                color="#52706a", font_size="0.82rem"),
                    spacing="2", width="100%",
                ),
                rx.cond(State.error_message != "", rx.text(State.error_message, color="#bd3e45", font_size="0.85rem")),
                rx.button(
                    "Criar conta", on_click=State.submit_signup, width="100%", height="50px", border_radius="10px",
                    background="#15856d", color="white", font_weight="600", _hover={"background": "#106f5b"},
                ),
                spacing="3", width="100%",
            ),
            rx.hstack(
                rx.text("Já possui uma conta?", color="#8aa09a", font_size="0.82rem"),
                rx.link("Entrar", href="/", color="#16866d", font_size="0.82rem", weight="medium"),
                justify="center", width="100%", spacing="2",
            ),
            spacing="5", width="100%", margin_top="38px",
        ),
        width="100%", max_width="465px", padding="42px", background="rgba(255, 255, 255, 0.94)",
        border="1px solid rgba(220, 235, 229, 0.9)", border_radius="20px",
        box_shadow="0 24px 70px rgba(28, 74, 64, 0.12)",
    )


def welcome_panel() -> rx.Component:
    return rx.vstack(
        brand(inverted=True), rx.spacer(),
        rx.vstack(
            rx.box(width="54px", height="4px", background="#5bdbbd", border_radius="full"),
            rx.heading("Pessoas no centro de tudo.", size="9", line_height="1.1", max_width="520px"),
            rx.text(
                "Uma experiência simples e completa para cuidar da sua equipe, horários e rotina de trabalho.",
                color="#c2d8d2", max_width="480px", font_size="1.1rem", line_height="1.65",
            ),
            spacing="5", align_items="start",
        ),
        rx.spacer(), rx.text("© 2026 Impacta Gestão de Pessoas", color="#9abbb2", font_size="0.8rem"),
        width="100%", height="100vh", padding="54px 72px",
        background="linear-gradient(145deg, #0a443b 0%, #126858 56%, #14836d 100%)",
        color="white", align_items="start",
    )


def navigation_item(label: str, href: str, active: bool = False) -> rx.Component:
    return rx.link(
        rx.box(
            rx.text(label, font_size="0.92rem", weight="medium", color="white" if active else "#a8c9c1"),
            width="100%", padding="11px 14px", border_radius="9px",
            background="rgba(255,255,255,0.14)" if active else "transparent",
        ),
        href=href, width="100%", text_decoration="none",
    )


def summary_card(title: str, value: str, description: str, accent: str) -> rx.Component:
    return rx.box(
        rx.box(width="36px", height="4px", background=accent, border_radius="full"),
        rx.text(title, color="#708681", font_size="0.83rem", margin_top="18px"),
        rx.text(value, color="#183f37", font_size="1.6rem", weight="bold", margin_top="3px"),
        rx.text(description, color="#8aa09a", font_size="0.78rem", margin_top="5px"),
        background="white", border="1px solid #e1ece8", border_radius="14px", padding="20px",
        box_shadow="0 8px 24px rgba(24, 75, 63, 0.05)", width="100%",
    )


def event_row(time: str, title: str, detail: str, color: str) -> rx.Component:
    return rx.hstack(
        rx.box(width="10px", height="10px", border_radius="full", background=color, flex_shrink="0"),
        rx.vstack(
            rx.text(title, color="#244940", weight="medium", font_size="0.9rem"),
            rx.text(detail, color="#839690", font_size="0.78rem"),
            spacing="1", align_items="start",
        ),
        rx.text(time, color="#54736b", font_size="0.82rem", margin_left="auto"),
        width="100%", align="center", padding="12px 0",
    )


def dashboard() -> rx.Component:
    sidebar = rx.vstack(
        brand(inverted=True),
        rx.vstack(
            navigation_item("Visão geral", "/inicio", active=True),
            navigation_item("Meu horário", "/horario"),
            navigation_item("Minha equipe", "/equipe"),
            navigation_item("Solicitações", "/solicitacoes"),
            navigation_item("Perfil", "/perfil"),
            navigation_item("Colaboradores", "/colaboradores"),
            spacing="2", width="100%", margin_top="46px",
        ),
        rx.spacer(),
        rx.box(
            rx.text("PRECISA DE AJUDA?", color="#9fc7bd", font_size="0.66rem", letter_spacing="0.09em"),
            rx.text("Fale com o RH", color="white", weight="medium", margin_top="5px"),
            padding="15px", background="rgba(255,255,255,0.1)", border_radius="12px", width="100%",
        ),
        width="248px", min_height="100vh", padding="32px 20px", background="#103f37",
        display=["none", "none", "flex"], align_items="start",
    )

    header = rx.hstack(
        rx.vstack(
            rx.text("DOMINGO, 5 DE OUTUBRO", color="#78918a", font_size="0.72rem", letter_spacing="0.08em"),
            rx.heading("Olá, Marina!", size="7", color="#173e36"),
            spacing="1", align_items="start",
        ),
        rx.hstack(
            rx.box(rx.text("MN", color="#176f5d", weight="bold", font_size="0.82rem"), width="36px", height="36px",
                   border_radius="full", background="#d9f1ea", display="flex", align_items="center", justify_content="center"),
            rx.vstack(rx.text(rx.cond(State.user_name != "", State.user_name, "Marina Nunes"), color="#254a42", weight="medium", font_size="0.85rem"),
                      rx.text("Colaboradora", color="#82978f", font_size="0.72rem"), spacing="0", align_items="start"),
            rx.button("Sair", on_click=State.sign_out, variant="ghost", color="#58766e", size="2"),
            spacing="2", align="center",
        ),
        width="100%", justify="between", align="center",
    )

    time_card = rx.box(
        rx.hstack(
            rx.vstack(
                rx.text("JORNADA DE HOJE", color="#6d8780", font_size="0.72rem", letter_spacing="0.08em"),
                rx.text("Você está trabalhando", color="#1b453c", weight="bold", font_size="1.15rem", margin_top="7px"),
                rx.text("Entrada registrada às 08:04", color="#78918a", font_size="0.84rem", margin_top="3px"),
                spacing="0", align_items="start",
            ),
            rx.box(rx.text("EM JORNADA", color="#14745f", weight="bold", font_size="0.68rem"), padding="7px 10px",
                   border_radius="full", background="#dff5ed"),
            width="100%", justify="between", align="start",
        ),
        rx.hstack(
            rx.vstack(rx.text("05h 34min", color="#173e36", weight="bold", font_size="1.7rem"),
                      rx.text("horas trabalhadas", color="#81958f", font_size="0.78rem"), spacing="0", align_items="start"),
            rx.button("Registrar ponto", background="#15856d", color="white", height="42px", border_radius="9px",
                      _hover={"background": "#106f5b"}),
            width="100%", justify="between", align="end", margin_top="24px",
        ),
        background="linear-gradient(135deg, #eefaf5 0%, #ffffff 78%)", border="1px solid #d7ebe4",
        border_radius="16px", padding="24px", width="100%",
    )

    main = rx.vstack(
        header,
        rx.grid(
            summary_card("PRÓXIMO TURNO", "Seg · 08:00", "Presencial · 8h diárias", "#5989dc"),
            summary_card("BANCO DE HORAS", "+ 02h 15min", "Atualizado hoje", "#38b596"),
            summary_card("FÉRIAS", "12 dias", "Disponíveis para agendar", "#d69b4d"),
            columns=rx.breakpoints(initial="1", md="3"), spacing="4", width="100%",
        ),
        rx.grid(
            rx.vstack(time_card, spacing="0", width="100%"),
            rx.box(
                rx.hstack(rx.text("Próximos eventos", color="#20473e", weight="bold", font_size="1.05rem"),
                          rx.link("Ver agenda", href="#", color="#17846c", font_size="0.82rem", margin_left="auto"), width="100%"),
                event_row("10:00", "Reunião de equipe", "Sala Innovation · 2º andar", "#5286db"),
                rx.divider(border_color="#edf2f0"),
                event_row("12:00", "Início do intervalo", "Retorno previsto às 13:00", "#37b899"),
                rx.divider(border_color="#edf2f0"),
                event_row("Sex, 11", "Aniversário da empresa", "Evento institucional", "#d49a4a"),
                background="white", border="1px solid #e1ece8", border_radius="16px", padding="22px", width="100%",
            ),
            columns=rx.breakpoints(initial="1", lg="2"), spacing="4", width="100%",
        ),
        rx.box(
            rx.text("AÇÕES RÁPIDAS", color="#78918a", font_size="0.72rem", letter_spacing="0.08em"),
            rx.hstack(
                rx.button("Solicitar férias", variant="soft", color_scheme="green"),
                rx.button("Justificar ausência", variant="soft", color_scheme="green"),
                rx.button("Consultar holerite", variant="soft", color_scheme="green"),
                spacing="3", flex_wrap="wrap", margin_top="13px",
            ),
            background="white", border="1px solid #e1ece8", border_radius="14px", padding="20px", width="100%",
        ),
        spacing="6", width="100%", max_width="1180px", padding=["26px 18px", "34px", "42px"],
    )

    return rx.hstack(sidebar, rx.box(main, background="#f5f9f7", min_height="100vh", width="100%"), spacing="0", width="100%")


def app_sidebar(active: str) -> rx.Component:
    items = [
        ("Visão geral", "/inicio", "inicio"),
        ("Meu horário", "/horario", "horario"),
        ("Minha equipe", "/equipe", "equipe"),
        ("Solicitações", "/solicitacoes", "solicitacoes"),
        ("Perfil", "/perfil", "perfil"),
        ("Colaboradores", "/colaboradores", "colaboradores"),
    ]
    return rx.vstack(
        brand(inverted=True),
        rx.vstack(
            *[navigation_item(label, href, active == key) for label, href, key in items],
            spacing="2", width="100%", margin_top="46px",
        ),
        rx.spacer(),
        rx.box(
            rx.text("PRECISA DE AJUDA?", color="#9fc7bd", font_size="0.66rem", letter_spacing="0.09em"),
            rx.text("Fale com o RH", color="white", weight="medium", margin_top="5px"),
            padding="15px", background="rgba(255,255,255,0.1)", border_radius="12px", width="100%",
        ),
        width="248px", min_height="100vh", padding="32px 20px", background="#103f37",
        display=["none", "none", "flex"], align_items="start",
    )


def page_header(title: str, subtitle: str) -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.heading(title, size="7", color="#173e36"),
            rx.text(subtitle, color="#78918a", font_size="0.9rem"),
            spacing="1", align_items="start",
        ),
        rx.hstack(
            rx.box(rx.text("MN", color="#176f5d", weight="bold", font_size="0.82rem"), width="36px", height="36px",
                   border_radius="full", background="#d9f1ea", display="flex", align_items="center", justify_content="center"),
            rx.vstack(rx.text(rx.cond(State.user_name != "", State.user_name, "Marina Nunes"), color="#254a42", weight="medium", font_size="0.85rem"),
                      rx.text("Colaboradora", color="#82978f", font_size="0.72rem"), spacing="0", align_items="start"),
            rx.button("Sair", on_click=State.sign_out, variant="ghost", color="#58766e", size="2"),
            spacing="2", align="center",
        ),
        width="100%", justify="between", align="center",
    )


def panel(*children: rx.Component) -> rx.Component:
    return rx.box(
        *children, background="white", border="1px solid #e1ece8", border_radius="16px",
        padding="22px", width="100%", box_shadow="0 8px 24px rgba(24, 75, 63, 0.04)",
    )


def page_shell(active: str, title: str, subtitle: str, *content: rx.Component) -> rx.Component:
    return rx.hstack(
        app_sidebar(active),
        rx.box(
            rx.vstack(page_header(title, subtitle), *content, spacing="6", width="100%", max_width="1180px",
                      padding=["26px 18px", "34px", "42px"]),
            background="#f5f9f7", min_height="100vh", width="100%",
        ),
        spacing="0", width="100%",
    )


def schedule_row(day: str, hours: str, status: str) -> rx.Component:
    return rx.hstack(
        rx.text(day, color="#244940", weight="medium", width="30%"),
        rx.text(hours, color="#6f8781", font_size="0.88rem", width="40%"),
        rx.box(rx.text(status, color="#17745f", font_size="0.72rem", weight="bold"), padding="5px 9px",
               border_radius="full", background="#e0f4ed"),
        width="100%", padding="13px 0", align="center",
    )


def horario() -> rx.Component:
    calendar = panel(
        rx.hstack(rx.text("Meu horário semanal", color="#20473e", weight="bold", font_size="1.05rem"),
                  rx.button("Outubro 2026", variant="soft", color_scheme="green", margin_left="auto"), width="100%"),
        schedule_row("Segunda", "08:00 — 12:00 · 13:00 — 17:00", "Presencial"), rx.divider(border_color="#edf2f0"),
        schedule_row("Terça", "08:00 — 12:00 · 13:00 — 17:00", "Remoto"), rx.divider(border_color="#edf2f0"),
        schedule_row("Quarta", "08:00 — 12:00 · 13:00 — 17:00", "Presencial"), rx.divider(border_color="#edf2f0"),
        schedule_row("Quinta", "08:00 — 12:00 · 13:00 — 17:00", "Presencial"), rx.divider(border_color="#edf2f0"),
        schedule_row("Sexta", "08:00 — 12:00 · 13:00 — 17:00", "Remoto"),
    )
    balance = panel(
        rx.text("Resumo do período", color="#20473e", weight="bold", font_size="1.05rem"),
        rx.vstack(
            rx.hstack(rx.text("Horas previstas", color="#6d8780"), rx.text("176h", color="#244940", weight="bold", margin_left="auto"), width="100%"),
            rx.hstack(rx.text("Horas realizadas", color="#6d8780"), rx.text("178h 15min", color="#244940", weight="bold", margin_left="auto"), width="100%"),
            rx.hstack(rx.text("Saldo", color="#6d8780"), rx.text("+ 02h 15min", color="#17846c", weight="bold", margin_left="auto"), width="100%"),
            spacing="4", margin_top="22px", width="100%",
        ),
    )
    return page_shell("horario", "Meu horário", "Acompanhe sua escala, jornada e banco de horas.",
                      rx.grid(calendar, balance, columns=rx.breakpoints(initial="1", lg="2"), spacing="4", width="100%"))


def request_row(kind: str, period: str, status: str, tone: str) -> rx.Component:
    return rx.hstack(
        rx.vstack(rx.text(kind, color="#244940", weight="medium"), rx.text(period, color="#849791", font_size="0.78rem"), spacing="1", align_items="start"),
        rx.box(rx.text(status, color=tone, font_size="0.72rem", weight="bold"), padding="6px 10px", border_radius="full", background="#edf6f3"),
        rx.text("Ver detalhes", color="#17846c", font_size="0.8rem", margin_left="auto"),
        width="100%", padding="12px 0", align="center",
    )


def solicitacoes() -> rx.Component:
    requests = panel(
        rx.hstack(rx.text("Minhas solicitações", color="#20473e", weight="bold", font_size="1.05rem"),
                  rx.button("Nova solicitação", background="#15856d", color="white", margin_left="auto"), width="100%"),
        request_row("Férias", "14 a 25 de dezembro · 12 dias", "Em análise", "#b77b24"), rx.divider(border_color="#edf2f0"),
        request_row("Ajuste de ponto", "03 de outubro · Entrada", "Aprovado", "#17745f"), rx.divider(border_color="#edf2f0"),
        request_row("Comprovante médico", "18 de setembro · 1 dia", "Concluído", "#17745f"),
    )
    vacation = panel(
        rx.text("Férias", color="#20473e", weight="bold", font_size="1.05rem"),
        rx.text("12 dias disponíveis", color="#173e36", font_size="1.65rem", weight="bold", margin_top="20px"),
        rx.text("Período aquisitivo: 01/03/2026 a 28/02/2027", color="#82978f", font_size="0.8rem", margin_top="4px"),
        rx.button("Planejar férias", variant="soft", color_scheme="green", width="100%", margin_top="22px"),
    )
    return page_shell("solicitacoes", "Solicitações e férias", "Envie, acompanhe e consulte suas solicitações.",
                      rx.grid(requests, vacation, columns=rx.breakpoints(initial="1", lg="2"), spacing="4", width="100%"))


def person_row(name: str, role: str, status: str) -> rx.Component:
    initials = "".join(word[0] for word in name.split()[:2])
    return rx.hstack(
        rx.box(rx.text(initials, color="#176f5d", weight="bold", font_size="0.76rem"), width="38px", height="38px", border_radius="full",
               background="#d9f1ea", display="flex", align_items="center", justify_content="center"),
        rx.vstack(rx.text(name, color="#244940", weight="medium"), rx.text(role, color="#849791", font_size="0.78rem"), spacing="0", align_items="start"),
        rx.box(rx.text(status, color="#17745f", font_size="0.72rem", weight="bold"), padding="5px 9px", border_radius="full", background="#e0f4ed", margin_left="auto"),
        width="100%", padding="10px 0", align="center",
    )


def equipe() -> rx.Component:
    team = panel(
        rx.hstack(rx.text("Equipe de Produto", color="#20473e", weight="bold", font_size="1.05rem"),
                  rx.text("8 pessoas", color="#78918a", font_size="0.82rem", margin_left="auto"), width="100%"),
        person_row("Marina Nunes", "Analista de Produto", "Em jornada"), rx.divider(border_color="#edf2f0"),
        person_row("Rafael Costa", "Product Manager", "Em jornada"), rx.divider(border_color="#edf2f0"),
        person_row("Camila Souza", "UX Designer", "Remoto"), rx.divider(border_color="#edf2f0"),
        person_row("André Lima", "Desenvolvedor", "Férias"),
    )
    manager = panel(
        rx.text("Sua liderança", color="#20473e", weight="bold", font_size="1.05rem"),
        person_row("Rafael Costa", "Product Manager", "Disponível"),
        rx.button("Enviar mensagem", variant="soft", color_scheme="green", width="100%", margin_top="15px"),
    )
    return page_shell("equipe", "Minha equipe", "Conheça a composição e disponibilidade da sua equipe.",
                      rx.grid(team, manager, columns=rx.breakpoints(initial="1", lg="2"), spacing="4", width="100%"))


def perfil() -> rx.Component:
    personal = panel(
        rx.hstack(rx.text("Dados pessoais", color="#20473e", weight="bold", font_size="1.05rem"), rx.button("Editar", variant="ghost", color="#17846c", margin_left="auto"), width="100%"),
        rx.text("Marina Nunes", color="#244940", weight="medium", margin_top="20px"),
        rx.text("marina.nunes@impacta.com", color="#78918a", font_size="0.85rem", margin_top="5px"),
        rx.text("(11) 99999-0000", color="#78918a", font_size="0.85rem", margin_top="5px"),
    )
    professional = panel(
        rx.text("Informações profissionais", color="#20473e", weight="bold", font_size="1.05rem"),
        rx.vstack(
            rx.hstack(rx.text("Cargo", color="#78918a"), rx.text("Analista de Produto", color="#244940", weight="medium", margin_left="auto"), width="100%"),
            rx.hstack(rx.text("Departamento", color="#78918a"), rx.text("Produto", color="#244940", weight="medium", margin_left="auto"), width="100%"),
            rx.hstack(rx.text("Admissão", color="#78918a"), rx.text("01 de março de 2024", color="#244940", weight="medium", margin_left="auto"), width="100%"),
            spacing="4", margin_top="20px", width="100%",
        ),
    )
    documents = panel(rx.text("Documentos", color="#20473e", weight="bold", font_size="1.05rem"),
                      rx.text("Holerites, informes e documentos enviados pelo RH.", color="#78918a", font_size="0.84rem", margin_top="8px"),
                      rx.button("Ver documentos", variant="soft", color_scheme="green", margin_top="18px"))
    return page_shell("perfil", "Meu perfil", "Consulte e mantenha suas informações atualizadas.",
                      rx.grid(personal, professional, columns=rx.breakpoints(initial="1", lg="2"), spacing="4", width="100%"), documents)


def colaboradores() -> rx.Component:
    metrics = rx.grid(
        summary_card("COLABORADORES ATIVOS", "128", "4 admissões neste mês", "#38b596"),
        summary_card("EM FÉRIAS", "7", "Próximos 30 dias", "#d69b4d"),
        summary_card("PENDÊNCIAS", "5", "Solicitações aguardando análise", "#5989dc"),
        columns=rx.breakpoints(initial="1", md="3"), spacing="4", width="100%",
    )
    directory = panel(
        rx.hstack(rx.text("Colaboradores", color="#20473e", weight="bold", font_size="1.05rem"),
                  rx.button("Novo colaborador", background="#15856d", color="white", margin_left="auto"), width="100%"),
        rx.input(placeholder="Buscar por nome, cargo ou departamento", width="100%", margin_top="18px", background="#f8fbfa"),
        person_row("Marina Nunes", "Produto · Analista de Produto", "Ativo"), rx.divider(border_color="#edf2f0"),
        person_row("Rafael Costa", "Produto · Product Manager", "Ativo"), rx.divider(border_color="#edf2f0"),
        person_row("Camila Souza", "Design · UX Designer", "Ativo"), rx.divider(border_color="#edf2f0"),
        person_row("André Lima", "Tecnologia · Desenvolvedor", "Férias"),
    )
    return page_shell("colaboradores", "Gestão de colaboradores", "Administre pessoas, vínculos, departamentos e solicitações.", metrics, directory)


def index() -> rx.Component:
    return rx.hstack(
        rx.box(welcome_panel(), width="52%", display=["none", "none", "block"]),
        rx.flex(
            login_form(), width=["100%", "100%", "48%"], min_height="100vh",
            padding=["20px", "32px", "48px"], align="center", justify="center", background="#f4f9f7",
        ),
        width="100%", min_height="100vh", spacing="0",
    )


def signup() -> rx.Component:
    return rx.hstack(
        rx.box(welcome_panel(), width="52%", display=["none", "none", "block"]),
        rx.flex(
            signup_form(), width=["100%", "100%", "48%"], min_height="100vh",
            padding=["20px", "32px", "48px"], align="center", justify="center", background="#f4f9f7",
        ),
        width="100%", min_height="100vh", spacing="0",
    )


app = rx.App(
    theme=rx.theme(appearance="light", has_background=True, radius="large", accent_color="green")
)
app.add_page(index, title="Impacta | Gestão de Pessoas")
app.add_page(signup, route="/cadastro", title="Criar conta | Impacta")
app.add_page(dashboard, route="/inicio", title="Início | Impacta")
app.add_page(horario, route="/horario", title="Meu horário | Impacta")
app.add_page(solicitacoes, route="/solicitacoes", title="Solicitações | Impacta")
app.add_page(equipe, route="/equipe", title="Minha equipe | Impacta")
app.add_page(perfil, route="/perfil", title="Meu perfil | Impacta")
app.add_page(colaboradores, route="/colaboradores", title="Colaboradores | Impacta")
