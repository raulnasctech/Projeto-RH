// Delete PRODUTO record.
query "produto/{produto_id}" verb=DELETE {
  api_group = "Event Logs"

  input {
    int produto_id? filters=min:1
  }

  stack {
    db.del PRODUTO {
      field_name = "id"
      field_value = $input.produto_id
    }
  }

  response = null
  guid = "s403cLDfMuir47vKQQua9rMpgZw"
}