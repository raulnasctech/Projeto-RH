// Delete STATUS_TTOKENIZACAO record.
query "status_ttokenizacao/{status_ttokenizacao_id}" verb=DELETE {
  api_group = "Event Logs"

  input {
    int status_ttokenizacao_id? filters=min:1
  }

  stack {
    db.del STATUS_TTOKENIZACAO {
      field_name = "id"
      field_value = $input.status_ttokenizacao_id
    }
  }

  response = null
  guid = "SZjJQsaIceLvbOo-y-4jKV8L5UM"
}