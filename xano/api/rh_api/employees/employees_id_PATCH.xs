// Edit employees record
query "employees/{employees_id}" verb=PATCH {
  api_group = "rh_api"

  input {
    int employees_id? filters=min:1
    dblink {
      table = "employees"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch employees {
      field_name = "id"
      field_value = $input.employees_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $employees
  }

  response = $employees
  guid = "J-cb6D-rN9cq0LcErc42YgOlBP4"
}