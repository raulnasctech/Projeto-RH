// Edit departments record
query "departments/{departments_id}" verb=PATCH {
  api_group = "rh_api"
  auth = "user"

  input {
    int departments_id? filters=min:1
    text nome? filters=trim
  }

  stack {
    function.run "RH API/authorize employee manager" {
      input = {authenticated_user_id: $auth.id}
    } as $authorization

    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch departaments {
      field_name = "id"
      field_value = $input.departments_id
      data = $raw_input|filter_null|filter_empty_text
    } as $departments
  }

  response = {
    id: $departments.id,
    name: $departments.nome
  }
}