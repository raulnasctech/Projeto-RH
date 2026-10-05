// Get TRANSAÇÃO record
query "transa_o/{transa_o_id}" verb=GET {
  api_group = "Event Logs"

  input {
    int transa_o_id? filters=min:1
  }

  stack {
    db.get "TRANSAÇÃO" {
      field_name = "id"
      field_value = $input.transa_o_id
    } as $transa_o
  
    precondition ($transa_o != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $transa_o
  guid = "EnOwVN_X-zi7SA6zd1K_IoY_x5E"
}