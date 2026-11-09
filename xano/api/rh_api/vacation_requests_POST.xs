// Add vacation_requests record
query vacation_requests verb=POST {
  api_group = "rh_api"
  auth = "user"

  input {
    int employees_id filters=min:1
    date start_date
    date end_date
  }

  stack {
    function.run "RH API/authorize employee manager" {
      input = {authenticated_user_id: $auth.id}
    } as $authorization

    precondition ($input.start_date <= $input.end_date) {
      error_type = "badrequest"
      error = "A data de início não pode ser posterior à data de fim."
    }

    db.get employees {
      field_name = "id"
      field_value = $input.employees_id
      output = ["id"]
    } as $employee

    precondition ($employee != null) {
      error_type = "notfound"
      error = "O colaborador selecionado não está disponível."
    }

    db.add vacation_requests {
      data = {
        created_at: "now"
        employees_id: $input.employees_id
        start_date: $input.start_date
        end_date: $input.end_date
        status: "Pendente"
      }
    } as $vacation_requests
  }

  response = $vacation_requests
  guid = "PhMK_KSKsG-cjGbkYIZpzAJ9ZsU"
}