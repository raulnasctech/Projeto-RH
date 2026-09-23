// Query all SOLCANCELAMENTO records
query solcancelamento verb=GET {
  api_group = "Event Logs"

  input {
  }

  stack {
    db.query SOLCANCELAMENTO {
      return = {type: "list"}
    } as $solcancelamento
  }

  response = $solcancelamento
  guid = "yDOoLVhdfqaW7s35GGooN6tbmfc"
}