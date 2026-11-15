// List vacation requests for the authenticated employee
query my_vacation_requests verb=GET {
  api_group = "rh_api"
  auth = "user"

  input {
  }

  stack {
    db.query employees {
      where = $db.employees.user_id == $auth.id
      output = ["id", "status"]
      return = {type: "list"}
    } as $linked_employees

    precondition (($linked_employees|count) == 1) {
      error_type = "accessdenied"
      error = "A conta deve estar vinculada a exatamente um colaborador."
    }

    var $employee {
      value = $linked_employees.0
    }

    precondition (($employee.status|lower) == "ativo") {
      error_type = "accessdenied"
      error = "Somente colaboradores ativos podem consultar solicitações de férias."
    }

    db.query vacation_requests {
      where = $db.vacation_requests.employees_id == $employee.id
      sort = {created_at: "desc"}
      output = ["id", "employees_id", "start_date", "end_date", "status"]
      return = {type: "list"}
    } as $vacation_requests
  }

  response = $vacation_requests
  guid = "OZmDUuOFDi_D-r-3waOshEyvvWI"
}
