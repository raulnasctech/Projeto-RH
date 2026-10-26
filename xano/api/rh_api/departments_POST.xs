// Add departments record
query departments verb=POST {
  api_group = "rh_api"
  auth = "user"

  input {
    text nome filters=trim
  }

  stack {
    function.run "RH API/authorize employee manager" {
      input = {authenticated_user_id: $auth.id}
    } as $authorization

    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input

    precondition ($raw_input.nome != "") {
      error_type = "badrequest"
      error = "Informe o nome do departamento."
    }

    db.add departaments {
      enforce_hidden_fields = false
      data = {
        nome: $raw_input.nome
      }
    } as $departments
  }

  response = {
    id: $departments.id,
    name: $departments.nome
  }
}