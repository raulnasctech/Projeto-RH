// Add ENDERECO record
query endereco verb=POST {
  api_group = "Event Logs"

  input {
    dblink {
      table = "ENDERECO"
    }
  }

  stack {
    db.add ENDERECO {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $endereco
  }

  response = $endereco
  guid = "GQ-0OVZBfytWwxOvI5ew0bYIWe4"
}