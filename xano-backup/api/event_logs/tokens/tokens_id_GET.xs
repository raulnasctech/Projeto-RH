// Get tokens record
query "tokens/{tokens_id}" verb=GET {
  api_group = "Event Logs"

  input {
    int tokens_id? filters=min:1
  }

  stack {
    db.get tokens {
      field_name = "id"
      field_value = $input.tokens_id
    } as $tokens
  
    precondition ($tokens != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $tokens
  guid = "QZUt3yrhznOpTQTxqyNup8WJDgo"
}