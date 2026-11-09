// Excluir departamento somente pelo Gestor de RH.
query "departments/{departments_id}" verb=DELETE {
  api_group = "rh_api"
  auth = "user"

  input {
    int departments_id? filters=min:1
  }

  stack {
    function.run "RH API/authorize employee manager" {
      input = {authenticated_user_id: $auth.id}
    } as $authorization

    db.del departaments {
      field_name = "id"
      field_value = $input.departments_id
    }
  }

  response = null
  guid = "Pepp-tX_3yw9A_WOvNxeWt95Sfk"
}