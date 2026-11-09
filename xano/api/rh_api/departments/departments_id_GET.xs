// Consultar departamento para o Gestor de RH
query "departments/{departments_id}" verb=GET {
  api_group = "rh_api"
  auth = "user"

  input {
    int departments_id? filters=min:1
  }

  stack {
    function.run "RH API/authorize employee manager" {
      input = {authenticated_user_id: $auth.id}
    } as $authorization

    db.get departaments {
      field_name = "id"
      field_value = $input.departments_id
    } as $departments
  
    precondition ($departments != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = {
    id: $departments.id,
    name: $departments.nome
  }
}