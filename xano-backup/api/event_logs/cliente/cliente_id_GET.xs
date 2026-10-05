// Get CLIENTE record
query "cliente/{cliente_id}" verb=GET {
  api_group = "Event Logs"

  input {
    int cliente_id? filters=min:1
  }

  stack {
    db.get CLIENTE {
      field_name = "id"
      field_value = $input.cliente_id
    } as $cliente
  
    precondition ($cliente != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $cliente
  guid = "6Q5t6EFI6DyLvIgM1tGFwONtRRg"
}