// Get Colaboradores record
query "colaboradores/{colaboradores_id}" verb=GET {
  api_group = "Event Logs"

  input {
    int colaboradores_id? filters=min:1
  }

  stack {
    db.get Colaboradores {
      field_name = "id"
      field_value = $input.colaboradores_id
    } as $colaboradores
  
    precondition ($colaboradores != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $colaboradores
  guid = "oSO_JJWjHBd53ox-W6Gir56DT6g"
}