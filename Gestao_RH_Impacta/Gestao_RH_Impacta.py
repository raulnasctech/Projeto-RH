"""Tela de acesso do Sistema de Gestão de RH."""

import os
from datetime import date

import httpx
import reflex as rx
from dotenv import load_dotenv

from Gestao_RH_Impacta.auth_service import (
    AuthenticationError,
    SessionRejected,
    authenticate,
    get_authenticated_user,
)
from Gestao_RH_Impacta.employee_service import (
    EmployeeAccessDenied,
    EmployeeCreationError,
    EmployeeDirectoryError,
    create_employee,
    get_employee,
    get_employee_form_options,
    list_employees,
    update_employee,
)
from Gestao_RH_Impacta.department_service import (
    DepartmentAccessDenied,
    DepartmentError,
    create_department,
    list_departments,
    update_department,
)
from Gestao_RH_Impacta.vacation_service import (
    VacationAccessDenied,
    VacationRequest,
    VacationRequestError,
    count_current_vacation_employees,
    create_vacation_request,
    decide_vacation_request,
    list_vacation_requests,
)
from Gestao_RH_Impacta.work_schedule_service import (
    WorkScheduleAccessDenied,
    WorkScheduleError,
    empty_work_week,
    get_work_schedule,
    save_work_schedule,
)


load_dotenv()
XANO_AUTH_API_URL = os.getenv("XANO_AUTH_API_URL", "").rstrip("/")
XANO_RH_API_URL = os.getenv("XANO_RH_API_URL", "").rstrip("/")


class State(rx.State):
    """Estado do formulário de acesso."""

    email: str = ""
    _password: str = ""
    name: str = ""
    cpf: str = ""
    celular: str = ""
    show_password: bool = False
    error_message: str = ""
    _auth_token: str = ""
    _auth_user_name: str = ""
    _authenticated: bool = False
    _skip_next_auth_check: bool = False
    employee_rows: list[dict[str, str]] = []
    employee_active_count: str = ""
    employee_total_count: str = "0"
    employee_vacation_count: str = "0"
    vacation_count_status: str = "loading"
    employee_list_status: str = "loading"
    employee_list_error: str = ""
    employee_form_open: bool = False
    employee_form_status: str = "idle"
    employee_form_error: str = ""
    employee_form_success: str = ""
    employee_department_options: list[dict[str, str]] = []
    employee_user_options: list[dict[str, str]] = []
    employee_form_name: str = ""
    employee_form_user_id: str = ""
    employee_form_department_id: str = ""
    employee_form_job_title: str = ""
    employee_form_admission_date: str = ""
    edit_employee_open: bool = False
    edit_employee_id: str = ""
    edit_employee_name: str = ""
    edit_employee_job_title: str = ""
    edit_employee_status: str = "Ativo"
    edit_employee_status_state: str = "idle"
    edit_employee_error: str = ""
    department_rows: list[dict[str, str]] = []
    department_list_status: str = "loading"
    department_list_error: str = ""
    department_form_open: bool = False
    department_form_name: str = ""
    department_form_error: str = ""
    department_form_success: str = ""
    edit_department_open: bool = False
    edit_department_id: str = ""
    edit_department_name: str = ""
    edit_department_error: str = ""
    vacation_rows: list[dict[str, str]] = []
    vacation_list_status: str = "loading"
    vacation_list_error: str = ""
    vacation_form_employee_id: str = ""
    vacation_form_start_date: str = ""
    vacation_form_end_date: str = ""
    vacation_form_status: str = "idle"
    vacation_form_error: str = ""
    vacation_form_success: str = ""
    vacation_action_status: str = "idle"
    vacation_action_error: str = ""
    work_schedule_employee_id: str = ""
    work_schedule_id: str = ""
    work_schedule_days: list[dict[str, str]] = []
    work_schedule_saved_days: list[dict[str, str]] = []
    work_schedule_load_status: str = "idle"
    work_schedule_load_error: str = ""
    work_schedule_save_status: str = "idle"
    work_schedule_save_error: str = ""
    work_schedule_save_success: str = ""

    @rx.var
    def user_name(self) -> str:
        return self._auth_user_name

    @rx.var
    def is_authenticated(self) -> bool:
        return self._authenticated

    def set_email(self, email: str):
        self.email = email

    def set_password(self, password: str):
        self._password = password

    def set_name(self, name: str):
        self.name = name

    def set_cpf(self, cpf: str):
        self.cpf = cpf

    def set_celular(self, celular: str):
        self.celular = celular

    def set_employee_form_name(self, name: str):
        self.employee_form_name = name
        self.employee_form_error = ""

    def set_employee_form_user_id(self, user_id: str):
        self.employee_form_user_id = user_id
        self.employee_form_error = ""

    def set_employee_form_department_id(self, department_id: str):
        self.employee_form_department_id = department_id
        self.employee_form_error = ""

    def set_employee_form_job_title(self, job_title: str):
        self.employee_form_job_title = job_title
        self.employee_form_error = ""

    def set_employee_form_admission_date(self, admission_date: str):
        self.employee_form_admission_date = admission_date
        self.employee_form_error = ""

    def set_show_password(self, show_password: bool):
        self.show_password = show_password

    def handle_employee_form_open_change(self, is_open: bool):
        self.employee_form_open = is_open
        if not is_open and self.employee_form_status != "saving":
            self.employee_form_status = "idle"
            self.employee_form_error = ""

    def _validate_credentials(self) -> bool:
        if not self.email.strip() or not self._password:
            self.error_message = "Informe seu e-mail e sua senha para continuar."
            return False
        elif "@" not in self.email:
            self.error_message = "Digite um endereço de e-mail válido."
            return False
        if not XANO_AUTH_API_URL:
            self.error_message = "Configure a variável XANO_AUTH_API_URL para conectar ao Xano."
            return False
        return True

    async def _authenticate(self, endpoint: str, payload: dict[str, str]) -> bool:
        try:
            user = await authenticate(XANO_AUTH_API_URL, endpoint, payload)
        except AuthenticationError as error:
            self._clear_session()
            self._password = ""
            self.error_message = str(error)
            return False
        except httpx.HTTPError:
            self._clear_session()
            self._password = ""
            self.error_message = "N\u00e3o foi poss\u00edvel conectar ao Xano. Verifique a URL da API."
            return False

        self._auth_token = user.token
        self._auth_user_name = user.user_name
        self._authenticated = True
        self._skip_next_auth_check = True
        self._password = ""
        self.error_message = ""
        return True

    async def submit_login(self):
        """Autentica as credenciais no endpoint Xano e abre o painel."""
        if not self._validate_credentials():
            return
        if await self._authenticate(
            "/auth/login", {"email": self.email, "password": self._password}
        ):
            return rx.redirect("/inicio")
        return self._clear_password_input()

    async def submit_signup(self):
        """Cria o usuário no Xano e inicia sua sessão."""
        if not self.name.strip():
            self.error_message = "Informe seu nome para criar a conta."
            return
        if not self._validate_credentials():
            return
        if len(self._password) < 8:
            self.error_message = "A senha deve ter ao menos 8 caracteres."
            return
        if await self._authenticate(
            "/auth/signup",
            {
                "name": self.name,
                "email": self.email,
                "password": self._password,
                "cpf": self.cpf,
                "celular": self.celular,
            },
        ):
            return rx.redirect("/inicio")
        return self._clear_password_input()

    def _clear_password_input(self):
        return rx.call_script(
            "const input = document.getElementById('password-input'); "
            "if (input) input.value = '';"
        )

    def _clear_session(self):
        self._auth_token = ""
        self._auth_user_name = ""
        self._authenticated = False
        self._skip_next_auth_check = False
        self.employee_rows = []
        self.employee_active_count = ""
        self.employee_total_count = "0"
        self.employee_vacation_count = "0"
        self.vacation_count_status = "loading"
        self.employee_list_status = "loading"
        self.employee_list_error = ""
        self.employee_form_open = False
        self.employee_form_status = "idle"
        self.employee_form_error = ""
        self.employee_form_success = ""
        self.employee_department_options = []
        self.employee_user_options = []
        self.employee_form_name = ""
        self.employee_form_user_id = ""
        self.employee_form_department_id = ""
        self.employee_form_job_title = ""
        self.employee_form_admission_date = ""
        self.vacation_rows = []
        self.vacation_list_status = "loading"
        self.vacation_list_error = ""
        self.vacation_form_employee_id = ""
        self.vacation_form_start_date = ""
        self.vacation_form_end_date = ""
        self.vacation_form_status = "idle"
        self.vacation_form_error = ""
        self.vacation_form_success = ""
        self.vacation_action_status = "idle"
        self.vacation_action_error = ""
        self.work_schedule_employee_id = ""
        self.work_schedule_id = ""
        self.work_schedule_days = []
        self.work_schedule_saved_days = []
        self.work_schedule_load_status = "idle"
        self.work_schedule_load_error = ""
        self.work_schedule_save_status = "idle"
        self.work_schedule_save_error = ""
        self.work_schedule_save_success = ""

    async def require_auth(self):
        """Valida a sessao no Xano antes de apresentar paginas internas."""
        if not self._auth_token:
            self._clear_session()
            return rx.redirect("/")
        if self._skip_next_auth_check:
            self._skip_next_auth_check = False
            self._authenticated = True
            self.error_message = ""
            return
        try:
            user = await get_authenticated_user(XANO_AUTH_API_URL, self._auth_token)
        except SessionRejected:
            self._clear_session()
            self.error_message = "Sua sess\u00e3o expirou. Entre novamente."
            return rx.redirect("/")
        except AuthenticationError:
            self._authenticated = False
            self.error_message = "N\u00e3o foi poss\u00edvel validar sua sess\u00e3o no Xano."
            return rx.redirect("/")
        except httpx.HTTPError:
            self._authenticated = False
            self.error_message = "N\u00e3o foi poss\u00edvel conectar ao Xano para validar sua sess\u00e3o."
            return rx.redirect("/")

        self._auth_user_name = user.user_name
        self._authenticated = True
        self.error_message = ""

    async def load_employees(self):
        """Carrega a lista; a API protegida valida a sessão e o perfil."""
        if not self._auth_token:
            self._clear_session()
            yield rx.redirect("/")
            return

        self.employee_list_status = "loading"
        self.employee_active_count = ""
        self.employee_list_error = ""
        yield

        try:
            employees = await list_employees(XANO_RH_API_URL, self._auth_token)
        except EmployeeAccessDenied as error:
            try:
                await get_authenticated_user(XANO_AUTH_API_URL, self._auth_token)
            except SessionRejected:
                self._clear_session()
                self.error_message = "Sua sessão expirou. Entre novamente."
                self.employee_list_error = self.error_message
                self.employee_list_status = "error"
                yield rx.redirect("/")
                return
            except AuthenticationError:
                self.employee_list_error = (
                    "Não foi possível validar sua sessão para consultar colaboradores."
                )
                self.employee_list_status = "error"
            except httpx.HTTPError:
                self.employee_list_error = (
                    "Não foi possível verificar a autorização para consultar colaboradores."
                )
                self.employee_list_status = "error"
            else:
                self.employee_list_error = str(error)
                self.employee_list_status = "error"
        except EmployeeDirectoryError as error:
            self.employee_list_error = str(error)
            self.employee_list_status = "error"
        except httpx.HTTPError:
            self.employee_list_error = (
                "Não foi possível conectar ao Xano para carregar colaboradores."
            )
            self.employee_list_status = "error"
        else:
            self.employee_rows = [employee.as_dict() for employee in employees]
            self.employee_total_count = str(len(employees))
            self.employee_active_count = str(
                sum(employee.status == "Ativo" for employee in employees)
            )
            self.employee_list_status = "loaded" if employees else "empty"
        yield

    async def load_hr_data(self):
        """Carrega dados funcionais e solicitações para as telas do RH."""
        async for event in self.load_employees():
            yield event
        if not self._auth_token:
            return
        async for event in self.load_vacation_requests():
            yield event

    async def load_work_schedule_page(self):
        """Valida a sessão antes de carregar colaboradores para a tela."""
        redirect = await self.require_auth()
        if redirect is not None:
            yield redirect
            return
        async for event in self.load_employees():
            yield event

    async def select_work_schedule_employee(self, employee_id: str):
        """Carrega somente a jornada persistida do colaborador selecionado."""
        self.work_schedule_employee_id = employee_id
        self.work_schedule_id = ""
        self.work_schedule_days = []
        self.work_schedule_saved_days = []
        self.work_schedule_load_error = ""
        self.work_schedule_save_error = ""
        self.work_schedule_save_success = ""
        self.work_schedule_save_status = "idle"
        if not employee_id:
            self.work_schedule_load_status = "idle"
            return
        if not any(row["id"] == employee_id for row in self.employee_rows):
            self.work_schedule_load_status = "error"
            self.work_schedule_load_error = "Selecione um colaborador existente."
            return
        if not self._auth_token:
            self._clear_session()
            yield rx.redirect("/")
            return

        self.work_schedule_load_status = "loading"
        yield

        try:
            schedule = await get_work_schedule(
                XANO_RH_API_URL, self._auth_token, employee_id
            )
        except WorkScheduleAccessDenied as error:
            if self.work_schedule_employee_id != employee_id:
                return
            self.work_schedule_load_error = str(error)
            self.work_schedule_load_status = "error"
        except WorkScheduleError as error:
            if self.work_schedule_employee_id != employee_id:
                return
            self.work_schedule_load_error = str(error)
            self.work_schedule_load_status = "error"
        except httpx.HTTPError:
            if self.work_schedule_employee_id != employee_id:
                return
            self.work_schedule_load_error = (
                "Não foi possível conectar ao Xano para consultar a jornada."
            )
            self.work_schedule_load_status = "error"
        else:
            if self.work_schedule_employee_id != employee_id:
                return
            if schedule is None:
                self.work_schedule_days = empty_work_week()
                self.work_schedule_load_status = "empty"
            else:
                self.work_schedule_id = schedule.id
                self.work_schedule_days = [
                    dict(day) for day in schedule.days
                ]
                self.work_schedule_saved_days = [
                    dict(day) for day in schedule.days
                ]
                self.work_schedule_load_status = "loaded"

        yield

    def set_work_schedule_day_workday(self, day_name: str, is_workday: bool):
        if self.work_schedule_save_status == "saving":
            return
        self.work_schedule_days = [
            {
                **day,
                "is_workday": "true" if is_workday else "false",
                **(
                    {}
                    if is_workday
                    else {
                        "start_time": "",
                        "end_time": "",
                        "break_start_time": "",
                        "break_end_time": "",
                    }
                ),
            }
            if day["day"] == day_name
            else day
            for day in self.work_schedule_days
        ]
        self.work_schedule_save_error = ""
        self.work_schedule_save_success = ""
        if self.work_schedule_save_status == "saved":
            self.work_schedule_save_status = "idle"

    def set_work_schedule_day_field(
        self, day_name: str, field_name: str, value: str
    ):
        allowed_fields = {
            "start_time",
            "end_time",
            "break_start_time",
            "break_end_time",
        }
        if (
            self.work_schedule_save_status == "saving"
            or field_name not in allowed_fields
        ):
            return
        self.work_schedule_days = [
            {**day, field_name: value} if day["day"] == day_name else day
            for day in self.work_schedule_days
        ]
        self.work_schedule_save_error = ""
        self.work_schedule_save_success = ""
        if self.work_schedule_save_status == "saved":
            self.work_schedule_save_status = "idle"

    def restore_saved_work_schedule(self):
        if self.work_schedule_save_status == "saving":
            return
        if self.work_schedule_saved_days:
            self.work_schedule_days = [
                dict(day) for day in self.work_schedule_saved_days
            ]
        else:
            self.work_schedule_days = empty_work_week()
        self.work_schedule_save_error = ""
        self.work_schedule_save_success = ""
        self.work_schedule_save_status = "idle"

    async def submit_work_schedule(self):
        """Valida e salva a semana completa sem alterar a última versão confirmada."""
        if self.work_schedule_load_status not in {"empty", "loaded"}:
            self.work_schedule_save_error = (
                "Consulte uma jornada antes de tentar salvá-la."
            )
            self.work_schedule_save_status = "error"
            return
        if not any(
            row["id"] == self.work_schedule_employee_id
            for row in self.employee_rows
        ):
            self.work_schedule_save_error = "Selecione um colaborador existente."
            self.work_schedule_save_status = "error"
            return
        if not self._auth_token:
            self._clear_session()
            yield rx.redirect("/")
            return

        self.work_schedule_save_status = "saving"
        self.work_schedule_save_error = ""
        self.work_schedule_save_success = ""
        employee_id = self.work_schedule_employee_id
        yield

        try:
            schedule = await save_work_schedule(
                XANO_RH_API_URL,
                self._auth_token,
                employee_id,
                self.work_schedule_days,
                schedule_id=self.work_schedule_id,
            )
        except WorkScheduleAccessDenied as error:
            if self.work_schedule_employee_id != employee_id:
                return
            self.work_schedule_save_error = str(error)
            self.work_schedule_save_status = "error"
        except WorkScheduleError as error:
            if self.work_schedule_employee_id != employee_id:
                return
            self.work_schedule_save_error = str(error)
            self.work_schedule_save_status = "error"
        except httpx.HTTPError:
            if self.work_schedule_employee_id != employee_id:
                return
            self.work_schedule_save_error = (
                "Não foi possível conectar ao Xano para salvar a jornada."
            )
            self.work_schedule_save_status = "error"
        else:
            if self.work_schedule_employee_id != employee_id:
                return
            self.work_schedule_id = schedule.id
            self.work_schedule_days = [dict(day) for day in schedule.days]
            self.work_schedule_saved_days = [
                dict(day) for day in schedule.days
            ]
            self.work_schedule_load_status = "loaded"
            self.work_schedule_save_status = "saved"
            self.work_schedule_save_success = (
                "Jornada semanal salva e confirmada pelo Xano."
            )

        yield

    async def load_vacation_requests(self):
        """Carrega solicitações e atualiza o indicador com férias vigentes."""
        if not self._auth_token:
            self._clear_session()
            yield rx.redirect("/")
            return

        self.vacation_list_status = "loading"
        self.vacation_count_status = "loading"
        self.vacation_list_error = ""
        yield

        try:
            requests = await list_vacation_requests(
                XANO_RH_API_URL, self._auth_token
            )
        except VacationAccessDenied as error:
            try:
                await get_authenticated_user(XANO_AUTH_API_URL, self._auth_token)
            except SessionRejected:
                self._clear_session()
                self.error_message = "Sua sessão expirou. Entre novamente."
                self.vacation_list_error = self.error_message
                self.vacation_list_status = "error"
                self.vacation_count_status = "error"
                self.employee_vacation_count = "Indisponível"
                yield rx.redirect("/")
                return
            except AuthenticationError:
                self.vacation_list_error = (
                    "Não foi possível validar sua sessão para consultar férias."
                )
                self.vacation_list_status = "error"
                self.vacation_count_status = "error"
                self.employee_vacation_count = "Indisponível"
            except httpx.HTTPError:
                self.vacation_list_error = (
                    "Não foi possível verificar a autorização para consultar férias."
                )
                self.vacation_list_status = "error"
                self.vacation_count_status = "error"
                self.employee_vacation_count = "Indisponível"
            else:
                self.vacation_list_error = str(error)
                self.vacation_list_status = "error"
                self.vacation_count_status = "error"
                self.employee_vacation_count = "Indisponível"
        except VacationRequestError as error:
            self.vacation_list_error = str(error)
            self.vacation_list_status = "error"
            self.vacation_count_status = "error"
            self.employee_vacation_count = "Indisponível"
        except httpx.HTTPError:
            self.vacation_list_error = (
                "Não foi possível conectar ao Xano para carregar as férias."
            )
            self.vacation_list_status = "error"
            self.vacation_count_status = "error"
            self.employee_vacation_count = "Indisponível"
        else:
            self.vacation_rows = [request.as_dict() for request in requests]
            self.employee_vacation_count = str(
                count_current_vacation_employees(requests)
            )
            self.vacation_list_status = "loaded" if requests else "empty"
            self.vacation_count_status = "loaded"
        yield

    def set_vacation_form_employee_id(self, employee_id: str):
        self.vacation_form_employee_id = employee_id
        self.vacation_form_error = ""

    def set_vacation_form_start_date(self, start_date: str):
        self.vacation_form_start_date = start_date
        self.vacation_form_error = ""

    def set_vacation_form_end_date(self, end_date: str):
        self.vacation_form_end_date = end_date
        self.vacation_form_error = ""

    async def submit_vacation_request(self):
        """Registra no Xano uma solicitação de férias para um colaborador."""
        employee = next(
            (
                row
                for row in self.employee_rows
                if row["id"] == self.vacation_form_employee_id
            ),
            None,
        )
        if employee is None:
            self.vacation_form_error = "Selecione um colaborador existente."
            return
        try:
            start_date = date.fromisoformat(self.vacation_form_start_date)
            end_date = date.fromisoformat(self.vacation_form_end_date)
        except ValueError:
            self.vacation_form_error = "Informe um período de férias válido."
            return
        if start_date > end_date:
            self.vacation_form_error = (
                "A data de início não pode ser posterior à data de fim."
            )
            return
        if not self._auth_token:
            self._clear_session()
            yield rx.redirect("/")
            return

        self.vacation_form_status = "saving"
        self.vacation_form_error = ""
        self.vacation_form_success = ""
        yield

        try:
            request_id = await create_vacation_request(
                XANO_RH_API_URL,
                self._auth_token,
                self.vacation_form_employee_id,
                start_date.isoformat(),
                end_date.isoformat(),
            )
        except VacationAccessDenied as error:
            self.vacation_form_error = str(error)
            self.vacation_form_status = "error"
        except VacationRequestError as error:
            self.vacation_form_error = str(error)
            self.vacation_form_status = "error"
        except httpx.HTTPError:
            self.vacation_form_error = (
                "Não foi possível conectar ao Xano para cadastrar as férias."
            )
            self.vacation_form_status = "error"
        else:
            self.vacation_form_status = "success"
            if self.vacation_list_status in {"loaded", "empty"}:
                request = {
                    "id": request_id,
                    "employee_id": employee["id"],
                    "employee_name": employee["name"],
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "status": "Pendente",
                }
                self.vacation_rows = [
                    request,
                    *[
                        row
                        for row in self.vacation_rows
                        if row["id"] != request_id
                    ],
                ]
                self.vacation_list_status = "loaded"
                self.vacation_list_error = ""
                self.vacation_form_success = (
                    "Solicitação cadastrada como pendente."
                )
            else:
                self.vacation_form_success = (
                    "Solicitação cadastrada como pendente. "
                    "Atualize a listagem para consultar todos os registros."
                )
            self.vacation_form_employee_id = ""
            self.vacation_form_start_date = ""
            self.vacation_form_end_date = ""

        yield

    async def decide_vacation_request(self, request_id: str, status: str):
        """Registra a decisão do RH e atualiza a listagem confirmada."""
        current_request = next(
            (row for row in self.vacation_rows if row["id"] == request_id),
            None,
        )
        if current_request is None or current_request["status"] != "Pendente":
            self.vacation_action_error = (
                "A solicitação não está mais pendente. Atualize a listagem."
            )
            return
        if status not in {"Aprovada", "Rejeitada"}:
            self.vacation_action_error = "Selecione uma decisão válida."
            return
        if not self._auth_token:
            self._clear_session()
            yield rx.redirect("/")
            return

        self.vacation_action_status = "saving"
        self.vacation_action_error = ""
        yield

        try:
            await decide_vacation_request(
                XANO_RH_API_URL, self._auth_token, request_id, status
            )
        except VacationAccessDenied as error:
            self.vacation_action_error = str(error)
            self.vacation_action_status = "error"
        except VacationRequestError as error:
            self.vacation_action_error = str(error)
            self.vacation_action_status = "error"
        except httpx.HTTPError:
            self.vacation_action_error = (
                "Não foi possível conectar ao Xano para registrar a decisão."
            )
            self.vacation_action_status = "error"
        else:
            self.vacation_rows = [
                {**row, "status": status}
                if row["id"] == request_id
                else row
                for row in self.vacation_rows
            ]
            requests = [
                VacationRequest(
                    id=row["id"],
                    employee_id=row["employee_id"],
                    employee_name=row["employee_name"],
                    start_date=row["start_date"],
                    end_date=row["end_date"],
                    status=row["status"],
                )
                for row in self.vacation_rows
            ]
            self.employee_vacation_count = str(
                count_current_vacation_employees(requests)
            )
            self.vacation_count_status = "loaded"
            self.vacation_list_status = (
                "loaded" if self.vacation_rows else "empty"
            )
            self.vacation_action_status = "idle"

        yield

    async def open_employee_form(self):
        """Abre o cadastro e carrega opções autorizadas do backend."""
        if not self._auth_token:
            self._clear_session()
            yield rx.redirect("/")
            return

        self.employee_form_open = True
        self.employee_form_status = "loading"
        self.employee_form_error = ""
        self.employee_form_success = ""
        self.employee_department_options = []
        self.employee_user_options = []
        self.employee_form_name = ""
        self.employee_form_user_id = ""
        self.employee_form_department_id = ""
        self.employee_form_job_title = ""
        self.employee_form_admission_date = ""
        yield

        try:
            options = await get_employee_form_options(
                XANO_RH_API_URL, self._auth_token
            )
        except EmployeeAccessDenied as error:
            try:
                await get_authenticated_user(XANO_AUTH_API_URL, self._auth_token)
            except SessionRejected:
                self._clear_session()
                yield rx.redirect("/")
                return
            except AuthenticationError:
                self.employee_form_error = (
                    "Não foi possível validar sua sessão para carregar o cadastro."
                )
                self.employee_form_status = "error"
            except httpx.HTTPError:
                self.employee_form_error = (
                    "Não foi possível verificar a autorização para o cadastro."
                )
                self.employee_form_status = "error"
            else:
                self.employee_form_error = str(error)
                self.employee_form_status = "error"
        except EmployeeCreationError as error:
            self.employee_form_error = str(error)
            self.employee_form_status = "error"
        except httpx.HTTPError:
            self.employee_form_error = (
                "Não foi possível conectar ao Xano para carregar as opções."
            )
            self.employee_form_status = "error"
        else:
            self.employee_department_options = [
                option.as_dict() for option in options.departments
            ]
            self.employee_user_options = [
                option.as_dict() for option in options.users
            ]
            self.employee_form_status = "ready"

        yield

    async def submit_employee(self):
        """Valida e envia o cadastro de funcionário ao Xano."""
        if self.employee_form_status not in {"ready", "error"}:
            return
        if not self.employee_form_name.strip():
            self.employee_form_error = "Informe o nome do funcionário."
            return
        if not any(
            option["id"] == self.employee_form_user_id
            for option in self.employee_user_options
        ):
            self.employee_form_error = "Selecione uma conta existente."
            return
        if not any(
            option["id"] == self.employee_form_department_id
            for option in self.employee_department_options
        ):
            self.employee_form_error = "Selecione um departamento."
            return
        if self.employee_form_admission_date:
            try:
                date.fromisoformat(self.employee_form_admission_date)
            except ValueError:
                self.employee_form_error = (
                    "Informe uma data de admissão válida."
                )
                return

        if not self._auth_token:
            self._clear_session()
            yield rx.redirect("/")
            return

        self.employee_form_status = "saving"
        self.employee_form_error = ""
        self.employee_form_success = ""
        yield

        try:
            employee_id = await create_employee(
                XANO_RH_API_URL,
                self._auth_token,
                self.employee_form_name,
                self.employee_form_user_id,
                self.employee_form_department_id,
                self.employee_form_job_title,
                self.employee_form_admission_date,
            )
        except EmployeeAccessDenied as error:
            try:
                await get_authenticated_user(XANO_AUTH_API_URL, self._auth_token)
            except SessionRejected:
                self._clear_session()
                yield rx.redirect("/")
                return
            except AuthenticationError:
                self.employee_form_error = (
                    "Não foi possível validar sua sessão para cadastrar."
                )
                self.employee_form_status = "error"
            except httpx.HTTPError:
                self.employee_form_error = (
                    "Não foi possível verificar a autorização do cadastro."
                )
                self.employee_form_status = "error"
            else:
                self.employee_form_error = str(error)
                self.employee_form_status = "error"
        except EmployeeCreationError as error:
            self.employee_form_error = str(error)
            self.employee_form_status = "error"
        except httpx.HTTPError:
            self.employee_form_error = (
                "Não foi possível conectar ao Xano para cadastrar o funcionário."
            )
            self.employee_form_status = "error"
        else:
            try:
                employees = await list_employees(
                    XANO_RH_API_URL, self._auth_token
                )
            except (EmployeeDirectoryError, httpx.HTTPError):
                self.employee_form_status = "success"
                self.employee_form_success = (
                    "O Xano confirmou o cadastro, mas não foi possível "
                    "atualizar a listagem. Não cadastre o funcionário novamente."
                )
                self.employee_list_error = (
                    "Atualize e publique o GET /employees no Xano para "
                    "sincronizar a listagem e o total."
                )
                self.employee_list_status = "error"
            else:
                self.employee_rows = [
                    employee.as_dict() for employee in employees
                ]
                self.employee_active_count = str(
                    sum(employee.status == "Ativo" for employee in employees)
                )
                employee_confirmed = any(
                    employee.id == employee_id for employee in employees
                )
                self.employee_list_status = (
                    "loaded" if employees else "empty"
                )
                self.employee_list_error = ""
                self.employee_form_status = "success"
                if employee_confirmed:
                    self.employee_form_success = (
                        "Funcionário cadastrado e confirmado na listagem."
                    )
                else:
                    self.employee_form_success = (
                        "O Xano confirmou o cadastro, mas o GET /employees "
                        "não retornou esse funcionário. Publique a atualização "
                        "do endpoint no Xano; não cadastre novamente."
                    )
                    self.employee_list_status = "error"
                    self.employee_list_error = (
                        "A resposta do Xano ainda não inclui o funcionário "
                        "recém-cadastrado."
                    )

            self.employee_form_open = False
            self.employee_form_name = ""
            self.employee_form_user_id = ""
            self.employee_form_department_id = ""
            self.employee_form_job_title = ""
            self.employee_form_admission_date = ""
            yield

            return

        yield

    def set_edit_employee_name(self, name: str):
        self.edit_employee_name = name
        self.edit_employee_error = ""

    def set_edit_employee_job_title(self, title: str):
        self.edit_employee_job_title = title
        self.edit_employee_error = ""

    def set_edit_employee_status(self, status: str):
        self.edit_employee_status = status
        self.edit_employee_error = ""

    def handle_edit_employee_open_change(self, is_open: bool):
        self.edit_employee_open = is_open
        if not is_open and self.edit_employee_status_state != "saving":
            self.edit_employee_status_state = "idle"
            self.edit_employee_error = ""

    async def open_edit_employee(self, employee_id: str):
        if not self._auth_token:
            self._clear_session()
            yield rx.redirect("/")
            return

        self.edit_employee_id = employee_id
        self.edit_employee_open = True
        self.edit_employee_status_state = "loading"
        self.edit_employee_error = ""
        yield

        try:
            emp = await get_employee(XANO_RH_API_URL, self._auth_token, employee_id)
        except Exception as error:
            self.edit_employee_error = str(error)
            self.edit_employee_status_state = "error"
        else:
            self.edit_employee_name = emp.name
            self.edit_employee_job_title = "" if emp.job_title == "Não informado" else emp.job_title
            self.edit_employee_status = emp.status if emp.status in {"Ativo", "Inativo", "Férias"} else "Ativo"
            self.edit_employee_status_state = "ready"

        yield

    async def submit_edit_employee(self):
        if not self.edit_employee_name.strip():
            self.edit_employee_error = "O nome não pode estar vazio."
            return
        if not self._auth_token:
            self._clear_session()
            yield rx.redirect("/")
            return

        self.edit_employee_status_state = "saving"
        self.edit_employee_error = ""
        yield

        try:
            await update_employee(
                XANO_RH_API_URL,
                self._auth_token,
                self.edit_employee_id,
                name=self.edit_employee_name,
                job_title=self.edit_employee_job_title,
                status=self.edit_employee_status,
            )
        except Exception as error:
            self.edit_employee_error = str(error)
            self.edit_employee_status_state = "error"
        else:
            try:
                employees = await list_employees(XANO_RH_API_URL, self._auth_token)
            except Exception:
                pass
            else:
                self.employee_rows = [e.as_dict() for e in employees]
                self.employee_active_count = str(
                    sum(e.status == "Ativo" for e in employees)
                )
            self.edit_employee_open = False
            self.edit_employee_status_state = "idle"

        yield

    def set_department_form_name(self, name: str):
        self.department_form_name = name
        self.department_form_error = ""

    def set_edit_department_name(self, name: str):
        self.edit_department_name = name
        self.edit_department_error = ""

    def handle_department_form_open_change(self, is_open: bool):
        self.department_form_open = is_open
        if not is_open:
            self.department_form_name = ""
            self.department_form_error = ""

    def handle_edit_department_open_change(self, is_open: bool):
        self.edit_department_open = is_open
        if not is_open:
            self.edit_department_error = ""

    async def load_departments(self):
        if not self._auth_token:
            self._clear_session()
            yield rx.redirect("/")
            return

        self.department_list_status = "loading"
        self.department_list_error = ""
        yield

        try:
            depts = await list_departments(XANO_RH_API_URL, self._auth_token)
        except DepartmentAccessDenied as error:
            self.department_list_error = str(error)
            self.department_list_status = "error"
        except DepartmentError as error:
            self.department_list_error = str(error)
            self.department_list_status = "error"
        except httpx.HTTPError:
            self.department_list_error = "Não foi possível conectar ao Xano."
            self.department_list_status = "error"
        else:
            self.department_rows = depts
            self.department_list_status = "loaded" if depts else "empty"

        yield

    async def open_department_form(self):
        if not self._auth_token:
            self._clear_session()
            yield rx.redirect("/")
            return
        self.department_form_name = ""
        self.department_form_error = ""
        self.department_form_success = ""
        self.department_form_open = True
        yield

    async def submit_department(self):
        if not self.department_form_name.strip():
            self.department_form_error = "O nome do departamento não pode estar vazio."
            return
        if not self._auth_token:
            self._clear_session()
            yield rx.redirect("/")
            return

        self.department_form_error = ""
        yield

        try:
            department_id = await create_department(
                XANO_RH_API_URL, self._auth_token, self.department_form_name
            )
        except DepartmentAccessDenied as error:
            self.department_form_error = str(error)
        except DepartmentError as error:
            self.department_form_error = str(error)
        except httpx.HTTPError:
            self.department_form_error = "Não foi possível conectar ao Xano para cadastrar o departamento."
        else:
            self.department_rows = [
                *self.department_rows,
                {
                    "id": str(department_id),
                    "name": self.department_form_name.strip(),
                },
            ]
            self.department_list_status = "loaded"
            self.department_list_error = ""
            self.department_form_open = False
            self.department_form_name = ""
            self.department_form_success = "Departamento cadastrado com sucesso."

        yield

    async def open_edit_department(self, dept_id: str, dept_name: str):
        if not self._auth_token:
            self._clear_session()
            yield rx.redirect("/")
            return
        self.edit_department_id = dept_id
        self.edit_department_name = dept_name
        self.edit_department_error = ""
        self.department_form_success = ""
        self.edit_department_open = True
        yield

    async def submit_edit_department(self):
        if not self.edit_department_name.strip():
            self.edit_department_error = "O nome não pode estar vazio."
            return
        if not self._auth_token:
            self._clear_session()
            yield rx.redirect("/")
            return

        self.edit_department_error = ""
        yield

        try:
            await update_department(
                XANO_RH_API_URL,
                self._auth_token,
                self.edit_department_id,
                self.edit_department_name,
            )
        except DepartmentAccessDenied as error:
            self.edit_department_error = str(error)
        except DepartmentError as error:
            self.edit_department_error = str(error)
        except httpx.HTTPError:
            self.edit_department_error = "Não foi possível conectar ao Xano para atualizar o departamento."
        else:
            updated_name = self.edit_department_name.strip()
            self.department_rows = [
                {
                    "id": department["id"],
                    "name": updated_name
                    if department["id"] == self.edit_department_id
                    else department["name"],
                }
                for department in self.department_rows
            ]
            self.department_list_status = "loaded" if self.department_rows else "empty"
            self.department_list_error = ""
            self.edit_department_open = False
            self.department_form_success = "Departamento atualizado com sucesso."

        yield

    def sign_out(self):
        self._clear_session()
        self._password = ""
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
                        id="password-input", on_change=State.set_password,
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
                        id="password-input", on_change=State.set_password, **field_style,
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


def vacation_summary_card() -> rx.Component:
    return rx.cond(
        State.vacation_count_status == "loading",
        summary_card(
            "COLABORADORES EM FÉRIAS",
            "Carregando...",
            "Consultando solicitações aprovadas",
            "#d69b4d",
        ),
        rx.cond(
            State.vacation_count_status == "error",
            summary_card(
                "COLABORADORES EM FÉRIAS",
                "Indisponível",
                "Não foi possível carregar os dados",
                "#d69b4d",
            ),
            summary_card(
                "COLABORADORES EM FÉRIAS",
                State.employee_vacation_count,
                "Férias aprovadas em andamento",
                "#d69b4d",
            ),
        ),
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
            navigation_item("Colaboradores", "/colaboradores"),
            navigation_item("Departamentos", "/departamentos"),
            navigation_item("Jornadas", "/jornadas"),
            navigation_item("Férias", "/ferias"),
            navigation_item("Perfil", "/perfil"),
            spacing="2", width="100%", margin_top="46px",
        ),
        rx.spacer(),
        rx.box(
            rx.text("PRECISA DE AJUDA?", color="#9fc7bd", font_size="0.66rem", letter_spacing="0.09em"),
            rx.text("Suporte RH", color="white", weight="medium", margin_top="5px"),
            padding="15px", background="rgba(255,255,255,0.1)", border_radius="12px", width="100%",
        ),
        width="248px", min_height="100vh", padding="32px 20px", background="#103f37",
        display=["none", "none", "flex"], align_items="start",
    )

    header = rx.hstack(
        rx.vstack(
            rx.text("PAINEL DO GESTOR DE RH", color="#78918a", font_size="0.72rem", letter_spacing="0.08em"),
            rx.heading("Visão geral da empresa", size="7", color="#173e36"),
            spacing="1", align_items="start",
        ),
        rx.hstack(
            rx.box(rx.text("RH", color="#176f5d", weight="bold", font_size="0.82rem"), width="36px", height="36px",
                   border_radius="full", background="#d9f1ea", display="flex", align_items="center", justify_content="center"),
            rx.vstack(rx.text(rx.cond(State.user_name != "", State.user_name, "Gestor(a)"), color="#254a42", weight="medium", font_size="0.85rem"),
                      rx.text("Gestor RH", color="#82978f", font_size="0.72rem"), spacing="0", align_items="start"),
            rx.button("Sair", on_click=State.sign_out, variant="ghost", color="#58766e", size="2"),
            spacing="2", align="center",
        ),
        width="100%", justify="between", align="center",
    )

    main = rx.vstack(
        header,
        rx.grid(
            summary_card("TOTAL COLABORADORES", State.employee_total_count, "Cadastrados no sistema", "#15856d"),
            vacation_summary_card(),
            columns=rx.breakpoints(initial="1", md="2"), spacing="4", width="100%",
        ),
        rx.box(
            rx.text("AÇÕES RÁPIDAS", color="#78918a", font_size="0.72rem", letter_spacing="0.08em"),
            rx.hstack(
                rx.link(rx.button("Gerenciar colaboradores", background="#15856d", color="white"), href="/colaboradores"),
                rx.link(rx.button("Gerenciar departamentos", variant="soft", color_scheme="green"), href="/departamentos"),
                rx.link(rx.button("Gerenciar jornadas", variant="soft", color_scheme="green"), href="/jornadas"),
                rx.link(rx.button("Gerenciar férias", variant="soft", color_scheme="green"), href="/ferias"),
                spacing="3", flex_wrap="wrap", margin_top="13px",
            ),
            background="white", border="1px solid #e1ece8", border_radius="14px", padding="22px", width="100%",
            box_shadow="0 8px 24px rgba(24, 75, 63, 0.04)",
        ),
        spacing="6", width="100%", max_width="1180px", padding=["26px 18px", "34px", "42px"],
    )

    return rx.hstack(sidebar, rx.box(main, background="#f5f9f7", min_height="100vh", width="100%"), spacing="0", width="100%")


def app_sidebar(active: str) -> rx.Component:
    items = [
        ("Visão geral", "/inicio", "inicio"),
        ("Colaboradores", "/colaboradores", "colaboradores"),
        ("Departamentos", "/departamentos", "departamentos"),
        ("Jornadas", "/jornadas", "jornadas"),
        ("Férias", "/ferias", "ferias"),
        ("Perfil", "/perfil", "perfil"),
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
    user_select = rx.select.root(
        rx.select.trigger(
            placeholder="Selecione uma conta existente",
            width="100%",
        ),
        rx.select.content(
            rx.select.group(
                rx.foreach(
                    State.employee_user_options,
                    lambda option: rx.select.item(
                        option["label"],
                        value=option["id"],
                    ),
                ),
            ),
        ),
        value=State.employee_form_user_id,
        on_change=State.set_employee_form_user_id,
        position="popper",
        width="100%",
    )
    department_select = rx.select.root(
        rx.select.trigger(
            placeholder="Selecione um departamento",
            width="100%",
        ),
        rx.select.content(
            rx.select.group(
                rx.foreach(
                    State.employee_department_options,
                    lambda option: rx.select.item(
                        option["label"],
                        value=option["id"],
                    ),
                ),
            ),
        ),
        value=State.employee_form_department_id,
        on_change=State.set_employee_form_department_id,
        position="popper",
        width="100%",
    )
    employee_form = rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Novo colaborador"),
            rx.dialog.description(
                "Informe o nome e os dados profissionais do colaborador."
            ),
            rx.cond(
                State.employee_form_status == "loading",
                rx.hstack(
                    rx.spinner(color="#15856d"),
                    rx.text("Carregando opções...", color="#78918a"),
                    spacing="3",
                    padding="20px 0",
                ),
                rx.vstack(
                    rx.cond(
                        State.employee_form_error != "",
                        rx.text(
                            State.employee_form_error,
                            color="#a33b32",
                            width="100%",
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        State.employee_user_options == [],
                        rx.text(
                            "Não há contas disponíveis para vincular.",
                            color="#78918a",
                            width="100%",
                        ),
                        rx.fragment(),
                    ),
                    rx.vstack(
                        rx.text(
                            "Conta existente",
                            weight="medium",
                            color="#35534c",
                            font_size="0.9rem",
                        ),
                        user_select,
                        spacing="2",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text(
                            "Nome completo",
                            weight="medium",
                            color="#35534c",
                            font_size="0.9rem",
                        ),
                        rx.input(
                            placeholder="Ex.: Maria da Silva",
                            value=State.employee_form_name,
                            on_change=State.set_employee_form_name,
                            width="100%",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text(
                            "Departamento",
                            weight="medium",
                            color="#35534c",
                            font_size="0.9rem",
                        ),
                        department_select,
                        spacing="2",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text(
                            "Cargo (opcional)",
                            weight="medium",
                            color="#35534c",
                            font_size="0.9rem",
                        ),
                        rx.input(
                            placeholder="Ex.: Analista",
                            value=State.employee_form_job_title,
                            on_change=State.set_employee_form_job_title,
                            width="100%",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text(
                            "Data de admissão (opcional)",
                            weight="medium",
                            color="#35534c",
                            font_size="0.9rem",
                        ),
                        rx.input(
                            type="date",
                            value=State.employee_form_admission_date,
                            on_change=State.set_employee_form_admission_date,
                            width="100%",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.button(
                            "Cancelar",
                            type="button",
                            variant="soft",
                            color_scheme="gray",
                            on_click=State.handle_employee_form_open_change(
                                False
                            ),
                        ),
                        rx.button(
                            rx.cond(
                                State.employee_form_status == "saving",
                                "Salvando...",
                                "Salvar funcionário",
                            ),
                            type="button",
                            on_click=State.submit_employee,
                            disabled=(
                                (State.employee_form_status == "saving")
                                | (State.employee_department_options == [])
                                | (State.employee_user_options == [])
                            ),
                            background="#15856d",
                            color="white",
                        ),
                        justify="end",
                        width="100%",
                        spacing="3",
                        padding_top="12px",
                    ),
                    spacing="4",
                    width="100%",
                ),
            ),
            max_width="520px",
            width="calc(100vw - 32px)",
        ),
        open=State.employee_form_open,
        on_open_change=State.handle_employee_form_open_change,
    )
    edit_employee_dialog = rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Editar colaborador"),
            rx.dialog.description("Atualize os dados funcionais ou a situação do colaborador."),
            rx.cond(
                State.edit_employee_status_state == "loading",
                rx.hstack(
                    rx.spinner(color="#15856d"),
                    rx.text("Carregando dados...", color="#78918a"),
                    spacing="3",
                    padding="20px 0",
                ),
                rx.vstack(
                    rx.cond(
                        State.edit_employee_error != "",
                        rx.text(State.edit_employee_error, color="#a33b32", width="100%"),
                        rx.fragment(),
                    ),
                    rx.vstack(
                        rx.text("Nome completo", weight="medium", color="#35534c", font_size="0.9rem"),
                        rx.input(
                            value=State.edit_employee_name,
                            on_change=State.set_edit_employee_name,
                            width="100%",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Cargo", weight="medium", color="#35534c", font_size="0.9rem"),
                        rx.input(
                            value=State.edit_employee_job_title,
                            on_change=State.set_edit_employee_job_title,
                            width="100%",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Situação", weight="medium", color="#35534c", font_size="0.9rem"),
                        rx.select.root(
                            rx.select.trigger(width="100%"),
                            rx.select.content(
                                rx.select.item("Ativo", value="Ativo"),
                                rx.select.item("Inativo", value="Inativo"),
                                rx.select.item("Férias", value="Férias"),
                            ),
                            value=State.edit_employee_status,
                            on_change=State.set_edit_employee_status,
                            width="100%",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.button(
                            "Cancelar",
                            type="button",
                            variant="soft",
                            color_scheme="gray",
                            on_click=State.handle_edit_employee_open_change(False),
                        ),
                        rx.button(
                            rx.cond(
                                State.edit_employee_status_state == "saving",
                                "Salvando...",
                                "Salvar alterações",
                            ),
                            type="button",
                            on_click=State.submit_edit_employee,
                            disabled=State.edit_employee_status_state == "saving",
                            background="#15856d",
                            color="white",
                        ),
                        justify="end",
                        width="100%",
                        spacing="3",
                        padding_top="12px",
                    ),
                    spacing="4",
                    width="100%",
                ),
            ),
            max_width="520px",
            width="calc(100vw - 32px)",
        ),
        open=State.edit_employee_open,
        on_open_change=State.handle_edit_employee_open_change,
    )
    active_employees_card = rx.cond(
        State.employee_list_status == "loading",
        summary_card(
            "COLABORADORES ATIVOS",
            "Carregando...",
            "Consultando colaboradores",
            "#38b596",
        ),
        rx.cond(
            State.employee_list_status == "error",
            summary_card(
                "COLABORADORES ATIVOS",
                "Indisponível",
                "Não foi possível carregar os dados",
                "#38b596",
            ),
            summary_card(
                "COLABORADORES ATIVOS",
                State.employee_active_count,
                "Situação: Ativo",
                "#38b596",
            ),
        ),
    )
    metrics = rx.grid(
        active_employees_card,
        vacation_summary_card(),
        columns=rx.breakpoints(initial="1", md="2"), spacing="4", width="100%",
    )
    directory = panel(
        rx.hstack(rx.text("Colaboradores", color="#20473e", weight="bold", font_size="1.05rem"),
                  rx.button("Novo colaborador", on_click=State.open_employee_form, background="#15856d", color="white", margin_left="auto"), width="100%"),
        rx.cond(
            State.employee_form_success != "",
            rx.text(
                State.employee_form_success,
                color="#17745f",
                padding="12px 0 0",
            ),
            rx.fragment(),
        ),
        rx.input(placeholder="Buscar por nome, cargo ou departamento", width="100%", margin_top="18px", background="#f8fbfa"),
        rx.cond(
            (State.employee_list_status == "loading")
            & (State.employee_rows == []),
            rx.hstack(
                rx.spinner(color="#15856d"),
                rx.text("Carregando colaboradores...", color="#78918a"),
                spacing="3",
                padding="24px 0",
            ),
            rx.cond(
                State.employee_rows == [],
                rx.cond(
                    State.employee_list_status == "error",
                    rx.text(
                        State.employee_list_error,
                        color="#a33b32",
                        padding="20px 0",
                    ),
                    rx.text(
                        "Nenhum colaborador cadastrado.",
                        color="#78918a",
                        padding="20px 0",
                    ),
                ),
                rx.vstack(
                    rx.cond(
                        State.employee_list_status == "loading",
                        rx.text(
                            "Atualizando lista...",
                            color="#78918a",
                            font_size="0.8rem",
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        State.employee_list_status == "error",
                        rx.text(
                            State.employee_list_error,
                            color="#a33b32",
                            padding="8px 0",
                        ),
                        rx.fragment(),
                    ),
                    rx.foreach(
                        State.employee_rows,
                        lambda employee: rx.hstack(
                            rx.box(
                                rx.text(
                                    "RH",
                                    color="#176f5d",
                                    weight="bold",
                                    font_size="0.76rem",
                                ),
                                width="38px",
                                height="38px",
                                border_radius="full",
                                background="#d9f1ea",
                                display="flex",
                                align_items="center",
                                justify_content="center",
                                flex_shrink="0",
                            ),
                            rx.vstack(
                                rx.text(
                                    employee["name"],
                                    color="#244940",
                                    weight="medium",
                                ),
                                rx.text(
                                    employee["department"],
                                    " · ",
                                    employee["job_title"],
                                    " · Admissão: ",
                                    employee["admission_date"],
                                    color="#849791",
                                    font_size="0.78rem",
                                ),
                                spacing="0",
                                align_items="start",
                                min_width="0",
                            ),
                            rx.hstack(
                                rx.box(
                                    rx.text(
                                        employee["status"],
                                        color="#17745f",
                                        font_size="0.72rem",
                                        weight="bold",
                                    ),
                                    padding="5px 9px",
                                    border_radius="full",
                                    background="#e0f4ed",
                                ),
                                rx.button(
                                    "Editar",
                                    size="1",
                                    variant="soft",
                                    color_scheme="green",
                                    on_click=lambda: State.open_edit_employee(employee["id"]),
                                ),
                                spacing="2",
                                margin_left="auto",
                                align="center",
                                flex_shrink="0",
                            ),
                            width="100%",
                            padding="10px 0",
                            align="center",
                        ),
                    ),
                    spacing="0",
                    width="100%",
                ),
            ),
        ),
    )
    return page_shell(
        "colaboradores",
        "Gestão de colaboradores",
        "Administre pessoas, vínculos, departamentos e solicitações.",
        metrics,
        directory,
        employee_form,
        edit_employee_dialog,
    )


def index() -> rx.Component:
    return rx.hstack(
        rx.box(welcome_panel(), width="52%", display=["none", "none", "block"]),
        rx.flex(
            login_form(), width=["100%", "100%", "48%"], min_height="100vh",
            padding=["20px", "32px", "48px"], align="center", justify="center", background="#f4f9f7",
        ),
        width="100%", min_height="100vh", spacing="0",
    )


def protected_page(page: rx.Component) -> rx.Component:
    return rx.cond(
        State.is_authenticated,
        page,
        rx.center(rx.spinner(), min_height="100vh", width="100%"),
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


def departamentos() -> rx.Component:
    dept_form = rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Novo departamento"),
            rx.dialog.description("Informe o nome do novo departamento."),
            rx.vstack(
                rx.cond(
                    State.department_form_error != "",
                    rx.text(State.department_form_error, color="#a33b32", width="100%"),
                    rx.fragment(),
                ),
                rx.vstack(
                    rx.text("Nome do departamento", weight="medium", color="#35534c", font_size="0.9rem"),
                    rx.input(
                        placeholder="Ex.: Engenharia",
                        value=State.department_form_name,
                        on_change=State.set_department_form_name,
                        width="100%",
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.hstack(
                    rx.button(
                        "Cancelar",
                        type="button",
                        variant="soft",
                        color_scheme="gray",
                        on_click=State.handle_department_form_open_change(False),
                    ),
                    rx.button(
                        "Salvar departamento",
                        type="button",
                        on_click=State.submit_department,
                        background="#15856d",
                        color="white",
                    ),
                    justify="end",
                    width="100%",
                    spacing="3",
                    padding_top="12px",
                ),
                spacing="4",
                width="100%",
            ),
            max_width="480px",
            width="calc(100vw - 32px)",
        ),
        open=State.department_form_open,
        on_open_change=State.handle_department_form_open_change,
    )

    edit_dept_dialog = rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Editar departamento"),
            rx.dialog.description("Atualize o nome do departamento."),
            rx.vstack(
                rx.cond(
                    State.edit_department_error != "",
                    rx.text(State.edit_department_error, color="#a33b32", width="100%"),
                    rx.fragment(),
                ),
                rx.vstack(
                    rx.text("Nome do departamento", weight="medium", color="#35534c", font_size="0.9rem"),
                    rx.input(
                        value=State.edit_department_name,
                        on_change=State.set_edit_department_name,
                        width="100%",
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.hstack(
                    rx.button(
                        "Cancelar",
                        type="button",
                        variant="soft",
                        color_scheme="gray",
                        on_click=State.handle_edit_department_open_change(False),
                    ),
                    rx.button(
                        "Salvar alterações",
                        type="button",
                        on_click=State.submit_edit_department,
                        background="#15856d",
                        color="white",
                    ),
                    justify="end",
                    width="100%",
                    spacing="3",
                    padding_top="12px",
                ),
                spacing="4",
                width="100%",
            ),
            max_width="480px",
            width="calc(100vw - 32px)",
        ),
        open=State.edit_department_open,
        on_open_change=State.handle_edit_department_open_change,
    )

    directory = panel(
        rx.hstack(
            rx.text("Departamentos", color="#20473e", weight="bold", font_size="1.05rem"),
            rx.button("Novo departamento", on_click=State.open_department_form, background="#15856d", color="white", margin_left="auto"),
            width="100%",
        ),
        rx.cond(
            State.department_form_success != "",
            rx.text(State.department_form_success, color="#17745f", padding="12px 0 0"),
            rx.fragment(),
        ),
        rx.cond(
            State.department_list_status == "loading",
            rx.hstack(
                rx.spinner(color="#15856d"),
                rx.text("Carregando departamentos...", color="#78918a"),
                spacing="3",
                padding="24px 0",
            ),
            rx.cond(
                State.department_rows == [],
                rx.cond(
                    State.department_list_status == "error",
                    rx.text(State.department_list_error, color="#a33b32", padding="20px 0"),
                    rx.text("Nenhum departamento cadastrado.", color="#78918a", padding="20px 0"),
                ),
                rx.vstack(
                    rx.foreach(
                        State.department_rows,
                        lambda dept: rx.hstack(
                            rx.text(dept["name"], color="#244940", weight="medium"),
                            rx.button(
                                "Editar",
                                size="1",
                                variant="soft",
                                color_scheme="green",
                                on_click=lambda: State.open_edit_department(dept["id"], dept["name"]),
                                margin_left="auto",
                            ),
                            width="100%",
                            padding="12px 0",
                            border_bottom="1px solid #edf2f0",
                            align="center",
                        ),
                    ),
                    spacing="0",
                    width="100%",
                ),
            ),
        ),
    )

    return page_shell(
        "departamentos",
        "Gestão de departamentos",
        "Estrutura organizacional e setores da empresa.",
        directory,
        dept_form,
        edit_dept_dialog,
    )


def jornadas() -> rx.Component:
    employee_selector = panel(
        rx.text(
            "Colaborador",
            color="#20473e",
            weight="bold",
            font_size="1.05rem",
        ),
        rx.text(
            "Selecione uma pessoa para consultar ou configurar sua semana recorrente.",
            color="#78918a",
            font_size="0.86rem",
            margin_top="6px",
        ),
        rx.select.root(
            rx.select.trigger(width="100%"),
            rx.select.content(
                rx.foreach(
                    State.employee_rows,
                    lambda employee: rx.select.item(
                        employee["name"], value=employee["id"]
                    ),
                )
            ),
            value=State.work_schedule_employee_id,
            on_change=State.select_work_schedule_employee,
            placeholder="Selecione um colaborador",
            width="100%",
            margin_top="16px",
            disabled=(
                (State.work_schedule_load_status == "loading")
                | (State.work_schedule_save_status == "saving")
            ),
        ),
    )

    day_editor = panel(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "Jornada semanal",
                        color="#20473e",
                        weight="bold",
                        font_size="1.05rem",
                    ),
                    rx.text(
                        "Os horários são salvos para os sete dias de uma só vez.",
                        color="#78918a",
                        font_size="0.84rem",
                    ),
                    spacing="1",
                    align_items="start",
                ),
                rx.button(
                    "Restaurar última versão salva",
                    on_click=State.restore_saved_work_schedule,
                    variant="soft",
                    color_scheme="gray",
                    disabled=(
                        (State.work_schedule_saved_days == [])
                        | (State.work_schedule_save_status == "saving")
                    ),
                    margin_left="auto",
                ),
                width="100%",
                align="center",
                flex_wrap="wrap",
            ),
            rx.cond(
                State.work_schedule_load_status == "empty",
                rx.text(
                    "Este colaborador ainda não possui uma jornada. Configure os dias e salve.",
                    color="#78918a",
                    padding_top="12px",
                ),
                rx.fragment(),
            ),
            rx.cond(
                State.work_schedule_save_error != "",
                rx.text(
                    State.work_schedule_save_error,
                    color="#a33b32",
                    width="100%",
                    padding_top="10px",
                ),
                rx.fragment(),
            ),
            rx.cond(
                State.work_schedule_save_success != "",
                rx.text(
                    State.work_schedule_save_success,
                    color="#17745f",
                    width="100%",
                    padding_top="10px",
                ),
                rx.fragment(),
            ),
            rx.cond(
                State.work_schedule_save_error != "",
                rx.text(
                    rx.cond(
                        State.work_schedule_saved_days == [],
                        "Nenhuma jornada foi confirmada para este colaborador.",
                        "A última versão confirmada continua salva. Restaure-a se não quiser manter o rascunho.",
                    ),
                    color="#78918a",
                    font_size="0.82rem",
                    width="100%",
                ),
                rx.fragment(),
            ),
            rx.foreach(
                State.work_schedule_days,
                lambda day: rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.text(
                                day["label"],
                                color="#244940",
                                weight="bold",
                            ),
                            rx.checkbox(
                                "Dia trabalhado",
                                checked=day["is_workday"] == "true",
                                on_change=lambda value: State.set_work_schedule_day_workday(
                                    day["day"], value
                                ),
                                disabled=State.work_schedule_save_status == "saving",
                                color="#15856d",
                            ),
                            justify="between",
                            width="100%",
                            align="center",
                            flex_wrap="wrap",
                        ),
                        rx.cond(
                            day["is_workday"] == "true",
                            rx.grid(
                                rx.vstack(
                                    rx.text(
                                        "Entrada",
                                        color="#78918a",
                                        font_size="0.82rem",
                                    ),
                                    rx.input(
                                        type="time",
                                        value=day["start_time"],
                                        on_change=lambda value: State.set_work_schedule_day_field(
                                            day["day"], "start_time", value
                                        ),
                                        disabled=State.work_schedule_save_status
                                        == "saving",
                                        width="100%",
                                    ),
                                    spacing="2",
                                    align_items="start",
                                ),
                                rx.vstack(
                                    rx.text(
                                        "Saída",
                                        color="#78918a",
                                        font_size="0.82rem",
                                    ),
                                    rx.input(
                                        type="time",
                                        value=day["end_time"],
                                        on_change=lambda value: State.set_work_schedule_day_field(
                                            day["day"], "end_time", value
                                        ),
                                        disabled=State.work_schedule_save_status
                                        == "saving",
                                        width="100%",
                                    ),
                                    spacing="2",
                                    align_items="start",
                                ),
                                rx.vstack(
                                    rx.text(
                                        "Início do intervalo (opcional)",
                                        color="#78918a",
                                        font_size="0.82rem",
                                    ),
                                    rx.input(
                                        type="time",
                                        value=day["break_start_time"],
                                        on_change=lambda value: State.set_work_schedule_day_field(
                                            day["day"], "break_start_time", value
                                        ),
                                        disabled=State.work_schedule_save_status
                                        == "saving",
                                        width="100%",
                                    ),
                                    spacing="2",
                                    align_items="start",
                                ),
                                rx.vstack(
                                    rx.text(
                                        "Fim do intervalo (opcional)",
                                        color="#78918a",
                                        font_size="0.82rem",
                                    ),
                                    rx.input(
                                        type="time",
                                        value=day["break_end_time"],
                                        on_change=lambda value: State.set_work_schedule_day_field(
                                            day["day"], "break_end_time", value
                                        ),
                                        disabled=State.work_schedule_save_status
                                        == "saving",
                                        width="100%",
                                    ),
                                    spacing="2",
                                    align_items="start",
                                ),
                                columns=rx.breakpoints(initial="1", md="2"),
                                spacing="4",
                                width="100%",
                            ),
                            rx.text(
                                "Folga — nenhum horário será enviado.",
                                color="#78918a",
                                font_size="0.84rem",
                            ),
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    padding="16px 0",
                    border_bottom="1px solid #edf2f0",
                    width="100%",
                ),
            ),
            rx.button(
                rx.cond(
                    State.work_schedule_save_status == "saving",
                    "Salvando semana...",
                    "Salvar jornada semanal",
                ),
                on_click=State.submit_work_schedule,
                disabled=State.work_schedule_save_status == "saving",
                background="#15856d",
                color="white",
                margin_left="auto",
                margin_top="8px",
            ),
            spacing="4",
            width="100%",
            align_items="start",
        )
    )

    return page_shell(
        "jornadas",
        "Gestão de jornadas",
        "Configure os dias trabalhados, folgas e horários recorrentes por colaborador.",
        employee_selector,
        rx.cond(
            State.work_schedule_load_status == "loading",
            panel(
                rx.hstack(
                    rx.spinner(color="#15856d"),
                    rx.text("Consultando jornada no Xano...", color="#78918a"),
                    spacing="3",
                )
            ),
            rx.cond(
                State.work_schedule_load_status == "error",
                panel(
                    rx.text(
                        State.work_schedule_load_error,
                        color="#a33b32",
                    )
                ),
                rx.cond(
                    (State.work_schedule_load_status == "empty")
                    | (State.work_schedule_load_status == "loaded"),
                    day_editor,
                    rx.fragment(),
                ),
            ),
        ),
    )


def ferias() -> rx.Component:
    request_form = panel(
        rx.text(
            "Nova solicitação",
            color="#20473e",
            weight="bold",
            font_size="1.05rem",
        ),
        rx.cond(
            State.vacation_form_success != "",
            rx.text(
                State.vacation_form_success,
                color="#17745f",
                padding_top="12px",
            ),
            rx.fragment(),
        ),
        rx.cond(
            State.vacation_form_error != "",
            rx.text(
                State.vacation_form_error,
                color="#a33b32",
                padding_top="12px",
            ),
            rx.fragment(),
        ),
        rx.vstack(
            rx.text(
                "Colaborador",
                weight="medium",
                color="#35534c",
                font_size="0.9rem",
            ),
            rx.select.root(
                rx.select.trigger(width="100%"),
                rx.select.content(
                    rx.foreach(
                        State.employee_rows,
                        lambda employee: rx.select.item(
                            employee["name"], value=employee["id"]
                        ),
                    )
                ),
                value=State.vacation_form_employee_id,
                on_change=State.set_vacation_form_employee_id,
                placeholder="Selecione um colaborador",
                width="100%",
            ),
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "Início das férias",
                        weight="medium",
                        color="#35534c",
                        font_size="0.9rem",
                    ),
                    rx.input(
                        type="date",
                        value=State.vacation_form_start_date,
                        on_change=State.set_vacation_form_start_date,
                        width="100%",
                    ),
                    width="100%",
                    spacing="2",
                    align_items="start",
                ),
                rx.vstack(
                    rx.text(
                        "Fim das férias",
                        weight="medium",
                        color="#35534c",
                        font_size="0.9rem",
                    ),
                    rx.input(
                        type="date",
                        value=State.vacation_form_end_date,
                        on_change=State.set_vacation_form_end_date,
                        width="100%",
                    ),
                    width="100%",
                    spacing="2",
                    align_items="start",
                ),
                width="100%",
                spacing="4",
                flex_wrap="wrap",
            ),
            rx.button(
                rx.cond(
                    State.vacation_form_status == "saving",
                    "Salvando...",
                    "Cadastrar solicitação",
                ),
                on_click=State.submit_vacation_request,
                disabled=(
                    (State.vacation_form_status == "saving")
                    | (State.employee_rows == [])
                ),
                background="#15856d",
                color="white",
                margin_left="auto",
            ),
            width="100%",
            spacing="4",
            margin_top="18px",
        ),
    )

    requests_directory = panel(
        rx.hstack(
            rx.text(
                "Solicitações de férias",
                color="#20473e",
                weight="bold",
                font_size="1.05rem",
            ),
            rx.button(
                "Atualizar",
                on_click=State.load_vacation_requests,
                variant="soft",
                color_scheme="green",
                margin_left="auto",
            ),
            width="100%",
        ),
        rx.cond(
            State.vacation_action_error != "",
            rx.text(
                State.vacation_action_error,
                color="#a33b32",
                padding="12px 0",
            ),
            rx.fragment(),
        ),
        rx.cond(
            State.vacation_list_status == "loading",
            rx.hstack(
                rx.spinner(color="#15856d"),
                rx.text("Carregando solicitações...", color="#78918a"),
                spacing="3",
                padding="24px 0",
            ),
            rx.cond(
                State.vacation_list_status == "error",
                rx.text(
                    State.vacation_list_error,
                    color="#a33b32",
                    padding="20px 0",
                ),
                rx.cond(
                    State.vacation_rows == [],
                    rx.text(
                        "Nenhuma solicitação de férias cadastrada.",
                        color="#78918a",
                        padding="20px 0",
                    ),
                    rx.vstack(
                        rx.foreach(
                            State.vacation_rows,
                            lambda request: rx.hstack(
                                rx.vstack(
                                    rx.text(
                                        request["employee_name"],
                                        color="#244940",
                                        weight="medium",
                                    ),
                                    rx.text(
                                        request["start_date"],
                                        " a ",
                                        request["end_date"],
                                        color="#849791",
                                        font_size="0.82rem",
                                    ),
                                    spacing="1",
                                    align_items="start",
                                ),
                                rx.text(
                                    request["status"],
                                    color="#17745f",
                                    weight="medium",
                                    font_size="0.82rem",
                                ),
                                rx.cond(
                                    request["status"] == "Pendente",
                                    rx.hstack(
                                        rx.button(
                                            "Aprovar",
                                            size="1",
                                            on_click=lambda: State.decide_vacation_request(
                                                request["id"], "Aprovada"
                                            ),
                                            disabled=(
                                                State.vacation_action_status
                                                == "saving"
                                            ),
                                            background="#15856d",
                                            color="white",
                                        ),
                                        rx.button(
                                            "Rejeitar",
                                            size="1",
                                            on_click=lambda: State.decide_vacation_request(
                                                request["id"], "Rejeitada"
                                            ),
                                            disabled=(
                                                State.vacation_action_status
                                                == "saving"
                                            ),
                                            variant="soft",
                                            color_scheme="red",
                                        ),
                                        spacing="2",
                                    ),
                                    rx.fragment(),
                                ),
                                width="100%",
                                padding="12px 0",
                                border_bottom="1px solid #edf2f0",
                                align="center",
                                justify="between",
                                flex_wrap="wrap",
                                spacing="3",
                            ),
                        ),
                        spacing="0",
                        width="100%",
                    ),
                ),
            ),
        ),
    )

    return page_shell(
        "ferias",
        "Gestão de férias",
        "Cadastre períodos e decida solicitações dos colaboradores.",
        vacation_summary_card(),
        request_form,
        requests_directory,
    )


app = rx.App(
    theme=rx.theme(appearance="light", has_background=True, radius="large", accent_color="green")
)
app.add_page(
    index,
    title="Impacta | Gestão de Pessoas",
)
app.add_page(
    signup,
    route="/cadastro",
    title="Criar conta | Impacta",
)
app.add_page(
    protected_page(dashboard()),
    route="/inicio",
    title="Início | Impacta",
    on_load=State.load_hr_data,
)
app.add_page(
    protected_page(perfil()),
    route="/perfil",
    title="Meu perfil | Impacta",
    on_load=State.require_auth,
)
app.add_page(
    protected_page(colaboradores()),
    route="/colaboradores",
    title="Colaboradores | Impacta",
    on_load=State.load_hr_data,
)
app.add_page(
    protected_page(departamentos()),
    route="/departamentos",
    title="Departamentos | Impacta",
    on_load=State.load_departments,
)
app.add_page(
    protected_page(jornadas()),
    route="/jornadas",
    title="Gestão de jornadas | Impacta",
    on_load=State.load_work_schedule_page,
)
app.add_page(
    protected_page(ferias()),
    route="/ferias",
    title="Gestão de férias | Impacta",
    on_load=State.load_hr_data,
)
