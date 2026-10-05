// Add SOLCANCELAMENTO record
query solcancelamento verb=POST {
  api_group = "Event Logs"

  input {
    dblink {
      table = "SOLCANCELAMENTO"
    }
  }

  stack {
    db.add SOLCANCELAMENTO {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $solcancelamento
  }

  response = $solcancelamento
  guid = "q43lZLfrUh6lUmbWcVnZql8fc9M"
}