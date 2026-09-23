// Delete CEP record.
query "cep/{cep_id}" verb=DELETE {
  api_group = "Event Logs"

  input {
    int cep_id? filters=min:1
  }

  stack {
    db.del CEP {
      field_name = "id"
      field_value = $input.cep_id
    }
  }

  response = null
  guid = "rAWThDVG0-eJ4ns4KwvuYl4i3xk"
}