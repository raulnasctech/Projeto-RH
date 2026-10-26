"""Serviço de consulta de colaboradores no Xano."""

from dataclasses import dataclass
from typing import Any

import httpx

REQUEST_TIMEOUT_SECONDS = 12


class EmployeeDirectoryError(Exception):
    """Erro ao consultar ou validar a listagem de colaboradores."""


class EmployeeAccessDenied(EmployeeDirectoryError):
    """O Xano recusou a consulta por falta de permissão."""


class EmployeeCreationError(EmployeeDirectoryError):
    """Erro ao consultar opções ou cadastrar um funcionário."""


@dataclass(frozen=True)
class Employee:
    id: str
    name: str
    department: str
    job_title: str
    admission_date: str
    status: str

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "department": self.department,
            "job_title": self.job_title,
            "admission_date": self.admission_date,
            "status": self.status,
        }


@dataclass(frozen=True)
class EmployeeDepartmentOption:
    id: str
    name: str

    def as_dict(self) -> dict[str, str]:
        return {"id": self.id, "label": self.name}


@dataclass(frozen=True)
class EmployeeUserOption:
    id: str
    name: str

    def as_dict(self) -> dict[str, str]:
        return {"id": self.id, "label": f"{self.name} (conta #{self.id})"}


@dataclass(frozen=True)
class EmployeeFormOptions:
    departments: list[EmployeeDepartmentOption]
    users: list[EmployeeUserOption]


def _display_value(record: dict[str, Any], key: str) -> str:
    value = record.get(key)
    if value is None or value == "":
        return "Não informado"
    if not isinstance(value, str):
        raise EmployeeDirectoryError(
            "A API retornou um campo inválido para a listagem de colaboradores."
        )
    return value


def _employee_name(record: dict[str, Any]) -> str:
    value = record.get("employee_name")
    if value is None or value == "":
        value = record.get("name")
    if value is None or value == "":
        return "Não informado"
    if not isinstance(value, str):
        raise EmployeeDirectoryError(
            "A API retornou um campo inválido para a listagem de colaboradores."
        )
    return value


def _parse_employees(data: Any) -> list[Employee]:
    if not isinstance(data, list):
        raise EmployeeDirectoryError(
            "A API retornou um formato inválido para a listagem de colaboradores."
        )

    employees = []
    for record in data:
        if not isinstance(record, dict):
            raise EmployeeDirectoryError(
                "A API retornou um registro inválido de colaborador."
            )

        employee_id = record.get("id")
        if (
            not isinstance(employee_id, (int, str))
            or isinstance(employee_id, bool)
            or not str(employee_id).strip()
        ):
            raise EmployeeDirectoryError(
                "A API retornou um registro sem identificador válido."
            )

        employees.append(
            Employee(
                id=str(employee_id),
                name=_employee_name(record),
                department=_display_value(record, "department"),
                job_title=_display_value(record, "job_title"),
                admission_date=_display_value(record, "admissao"),
                status=_display_value(record, "status"),
            )
        )
    return employees


def _parse_option_id(record: dict[str, Any]) -> str:
    option_id = record.get("id")
    if (
        not isinstance(option_id, (int, str))
        or isinstance(option_id, bool)
        or not str(option_id).strip()
    ):
        raise EmployeeCreationError(
            "A API retornou uma opção sem identificador válido."
        )
    return str(option_id)


def _parse_form_options(data: Any) -> EmployeeFormOptions:
    if not isinstance(data, dict):
        raise EmployeeCreationError(
            "A API retornou um formato inválido para o formulário."
        )

    departments_data = data.get("departments")
    users_data = data.get("users")
    if (
        set(data) - {"users", "departments"}
        or not isinstance(departments_data, list)
    ):
        raise EmployeeCreationError(
            "A API retornou opções inválidas para o formulário."
        )
    if not isinstance(users_data, list):
        raise EmployeeCreationError(
            "Atualize a rota de opções no Xano para retornar contas e departamentos."
        )

    departments = []
    for record in departments_data:
        if not isinstance(record, dict):
            raise EmployeeCreationError(
                "A API retornou um departamento inválido para o formulário."
            )
        if set(record) - {"id", "nome"}:
            raise EmployeeCreationError(
                "A API retornou campos não permitidos para um departamento."
            )
        name = record.get("nome")
        if not isinstance(name, str) or not name.strip():
            raise EmployeeCreationError(
                "A API retornou dados inválidos de um departamento."
            )
        departments.append(
            EmployeeDepartmentOption(id=_parse_option_id(record), name=name)
        )

    users = []
    for record in users_data:
        if not isinstance(record, dict):
            raise EmployeeCreationError(
                "A API retornou uma conta inválida para o formulário."
            )
        name = record.get("name")
        if not isinstance(name, str) or not name.strip():
            raise EmployeeCreationError(
                "A API retornou dados inválidos de uma conta."
            )
        users.append(
            EmployeeUserOption(id=_parse_option_id(record), name=name.strip())
        )

    return EmployeeFormOptions(departments=departments, users=users)


def _validate_api_url(api_url: str) -> str:
    normalized_url = api_url.rstrip("/")
    if not normalized_url:
        raise EmployeeDirectoryError(
            "Configure a variável XANO_RH_API_URL para conectar à API de RH."
        )
    return normalized_url


def _raise_for_employee_response(response: httpx.Response, operation: str) -> None:
    if response.status_code in (401, 403):
        raise EmployeeAccessDenied(
            "Seu perfil não tem autorização para realizar esta operação."
        )
    if response.is_error:
        raise EmployeeCreationError(
            f"Não foi possível {operation} no Xano."
        )


async def get_employee_form_options(
    api_url: str, token: str
) -> EmployeeFormOptions:
    """Busca contas não associadas e departamentos para o formulário do RH."""
    normalized_url = _validate_api_url(api_url)
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.get(
            f"{normalized_url}/employee-form-options",
            headers={"Authorization": f"Bearer {token}"},
        )

    _raise_for_employee_response(response, "carregar opções de cadastro")
    try:
        data = response.json()
    except ValueError as error:
        raise EmployeeCreationError(
            "A API retornou uma resposta inválida para as opções do formulário."
        ) from error
    return _parse_form_options(data)


async def create_employee(
    api_url: str,
    token: str,
    name: str,
    user_id: str,
    department_id: str,
    job_title: str,
    admission_date: str,
) -> str:
    """Cria um funcionário associado a uma conta de acesso existente."""
    normalized_url = _validate_api_url(api_url)
    normalized_name = name.strip()
    if not normalized_name:
        raise EmployeeCreationError("Informe o nome do funcionário.")
    try:
        parsed_user_id = int(user_id)
    except (TypeError, ValueError) as error:
        raise EmployeeCreationError(
            "Selecione uma conta existente."
        ) from error
    if parsed_user_id < 1:
        raise EmployeeCreationError("Selecione uma conta existente.")
    try:
        parsed_department_id = int(department_id)
    except (TypeError, ValueError) as error:
        raise EmployeeCreationError(
            "Selecione um departamento válido."
        ) from error
    if parsed_department_id < 1:
        raise EmployeeCreationError(
            "Selecione um departamento válido."
        )

    payload: dict[str, Any] = {
        "name": normalized_name,
        "user_id": parsed_user_id,
        "departaments_id": parsed_department_id,
    }
    if job_title.strip():
        payload["job_title"] = job_title.strip()
    if admission_date.strip():
        payload["admissao"] = admission_date.strip()

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.post(
            f"{normalized_url}/employees",
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
        )

    _raise_for_employee_response(response, "cadastrar o funcionário")
    try:
        data = response.json()
    except ValueError as error:
        raise EmployeeCreationError(
            "A API retornou uma resposta inválida após o cadastro."
        ) from error
    if not isinstance(data, dict):
        raise EmployeeCreationError(
            "A API retornou uma confirmação inválida após o cadastro."
        )
    employee_id = data.get("id")
    if (
        not isinstance(employee_id, (int, str))
        or isinstance(employee_id, bool)
        or not str(employee_id).strip()
    ):
        raise EmployeeCreationError(
            "A API não confirmou o identificador do funcionário cadastrado."
        )
    return str(employee_id)


async def list_employees(api_url: str, token: str) -> list[Employee]:
    """Busca somente os campos aprovados para a lista do RH."""
    normalized_url = _validate_api_url(api_url)
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.get(
            f"{normalized_url}/employees",
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code in (401, 403):
        raise EmployeeAccessDenied(
            "Seu perfil não tem autorização para consultar colaboradores."
        )
    if response.is_error:
        raise EmployeeDirectoryError(
            "Não foi possível carregar os colaboradores do Xano."
        )

    try:
        data = response.json()
    except ValueError as error:
        raise EmployeeDirectoryError(
            "A API retornou uma resposta inválida para a listagem."
        ) from error

    return _parse_employees(data)


async def get_employee(api_url: str, token: str, employee_id: str) -> Employee:
    """Busca os detalhes de um funcionário específico."""
    normalized_url = _validate_api_url(api_url)
    try:
        parsed_id = int(employee_id)
    except (TypeError, ValueError) as error:
        raise EmployeeDirectoryError("Identificador de funcionário inválido.") from error

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.get(
            f"{normalized_url}/employees/{parsed_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code in (401, 403):
        raise EmployeeAccessDenied("Seu perfil não tem autorização para consultar este funcionário.")
    if response.status_code == 404:
        raise EmployeeDirectoryError("Funcionário não encontrado.")
    if response.is_error:
        raise EmployeeDirectoryError("Não foi possível carregar os detalhes do funcionário.")

    try:
        data = response.json()
    except ValueError as error:
        raise EmployeeDirectoryError("A API retornou uma resposta inválida para o funcionário.") from error

    if not isinstance(data, dict):
        raise EmployeeDirectoryError("A API retornou um formato inválido para o funcionário.")

    return Employee(
        id=str(data.get("id", "")),
        name=_employee_name(data),
        department=_display_value(data, "department"),
        job_title=_display_value(data, "job_title"),
        admission_date=_display_value(data, "admissao"),
        status=_display_value(data, "status"),
    )


async def update_employee(
    api_url: str,
    token: str,
    employee_id: str,
    name: str | None = None,
    job_title: str | None = None,
    status: str | None = None,
    department_id: str | None = None,
) -> None:
    """Atualiza dados de um funcionário existente."""
    normalized_url = _validate_api_url(api_url)
    try:
        parsed_id = int(employee_id)
    except (TypeError, ValueError) as error:
        raise EmployeeCreationError("Identificador de funcionário inválido.") from error

    payload: dict[str, Any] = {}
    if name is not None:
        norm_name = name.strip()
        if not norm_name:
            raise EmployeeCreationError("O nome do funcionário não pode estar vazio.")
        payload["name"] = norm_name
    if job_title is not None:
        payload["job_title"] = job_title.strip()
    if status is not None:
        norm_status = status.strip()
        if norm_status:
            payload["status"] = norm_status
    if department_id is not None:
        try:
            parsed_dept_id = int(department_id)
        except (TypeError, ValueError) as error:
            raise EmployeeCreationError("Selecione um departamento válido.") from error
        if parsed_dept_id < 1:
            raise EmployeeCreationError("Selecione um departamento válido.")
        payload["departaments_id"] = parsed_dept_id

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.patch(
            f"{normalized_url}/employees/{parsed_id}",
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
        )

    _raise_for_employee_response(response, "atualizar o funcionário")
