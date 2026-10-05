// Add STATUS_TRANSACAO record
query status_transacao verb=POST {
  api_group = "Event Logs"

  input {
    dblink {
      table = "STATUS_TRANSACAO"
    }
  }

  stack {
    db.add STATUS_TRANSACAO {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $status_transacao
  }

  response = $status_transacao
  guid = "hKX7rTwWsQE5colwSpLCKbSRAh4"
}