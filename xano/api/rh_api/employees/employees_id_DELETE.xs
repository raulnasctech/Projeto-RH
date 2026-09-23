// Delete employees record.
query "employees/{employees_id}" verb=DELETE {
  api_group = "rh_api"

  input {
    int employees_id? filters=min:1
  }

  stack {
    db.del employees {
      field_name = "id"
      field_value = $input.employees_id
    }
  }

  response = null
  guid = "PyHTMCT3KD-uPCXXAwEC7BYeH0s"
}