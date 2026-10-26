// Edit employees record
query "employees/{employees_id}" verb=PATCH {
  api_group = "rh_api"
  auth = "user"

  input {
    int employees_id? filters=min:1
  }

  stack {
    function.run "RH API/authorize employee manager" {
      input = {authenticated_user_id: $auth.id}
    } as $authorization

    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch employees {
      field_name = "id"
      field_value = $input.employees_id
      data = $raw_input|filter_null|filter_empty_text
    } as $employees
  }

  response = $employees
  guid = "J-cb6D-rN9cq0LcErc42YgOlBP4"
}