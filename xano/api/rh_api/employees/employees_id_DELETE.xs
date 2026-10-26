// Delete employees record.
query "employees/{employees_id}" verb=DELETE {
  api_group = "rh_api"
  auth = "user"

  input {
    int employees_id? filters=min:1
  }

  stack {
    function.run "RH API/authorize employee manager" {
      input = {authenticated_user_id: $auth.id}
    } as $authorization

    db.del employees {
      field_name = "id"
      field_value = $input.employees_id
    }
  }

  response = null
  guid = "PyHTMCT3KD-uPCXXAwEC7BYeH0s"
}