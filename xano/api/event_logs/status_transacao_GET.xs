// Query all STATUS_TRANSACAO records
query status_transacao verb=GET {
  api_group = "Event Logs"

  input {
  }

  stack {
    db.query STATUS_TRANSACAO {
      return = {type: "list"}
    } as $status_transacao
  }

  response = $status_transacao
  guid = "-VFdAbskgSZjBxg_tQct3KnqVW8"
}