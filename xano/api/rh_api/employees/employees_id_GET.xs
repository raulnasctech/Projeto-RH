// Get employees record
query "employees/{employees_id}" verb=GET {
  api_group = "rh_api"

  input {
    int employees_id? filters=min:1
  }

  stack {
    db.get employees {
      field_name = "id"
      field_value = $input.employees_id
    } as $employees
  
    precondition ($employees != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $employees
  guid = "18CrvnVwE0pvnuEtgeoORmN9ISA"
}