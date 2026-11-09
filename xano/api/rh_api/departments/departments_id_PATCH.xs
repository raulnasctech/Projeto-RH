// Editar departamento para o Gestor de RH
query "departments/{departments_id}" verb=PATCH {
  api_group = "rh_api"
  auth = "user"

  input {
    int departments_id? filters=min:1
    text nome filters=trim
  }

  stack {
    function.run "RH API/authorize employee manager" {
      input = {authenticated_user_id: $auth.id}
    } as $authorization

    precondition ($input.nome != "") {
      error_type = "badrequest"
      error = "Informe o nome do departamento."
    }

    db.get departaments {
      field_name = "id"
      field_value = $input.departments_id
    } as $existing_department

    precondition ($existing_department != null) {
      error_type = "notfound"
      error = "Departamento não encontrado."
    }

    db.patch departaments {
      field_name = "id"
      field_value = $input.departments_id
      data = {nome: $input.nome}
    } as $departments
  }

  response = {
    id: $departments.id,
    name: $departments.nome
  }
  guid = "X3gTRFgiE_k6oe4z5XYaafHY4co"
}