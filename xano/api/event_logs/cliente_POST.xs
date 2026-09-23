// Add CLIENTE record
query cliente verb=POST {
  api_group = "Event Logs"

  input {
    dblink {
      table = "CLIENTE"
    }
  }

  stack {
    db.add CLIENTE {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $cliente
  }

  response = $cliente
  guid = "grfaTqretcZ7LRCElUFtFbP4dtM"
}