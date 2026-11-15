// Create a vacation request for the authenticated employee
query my_vacation_requests verb=POST {
  api_group = "rh_api"
  auth = "user"

  input {
    date start_date
    date end_date
  }

  stack {
    precondition ($input.start_date <= $input.end_date) {
      error_type = "badrequest"
      error = "A data de início não pode ser posterior à data de fim."
    }

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
      error = "Somente colaboradores ativos podem solicitar férias."
    }

    db.add vacation_requests {
      data = {
        created_at: "now"
        employees_id: $employee.id
        start_date: $input.start_date
        end_date: $input.end_date
        status: "Pendente"
      }
    } as $vacation_request
  }

  response = $vacation_request
  guid = "K3koXxJ4m8mN5KTM8rSYO3lgUDk"
}
