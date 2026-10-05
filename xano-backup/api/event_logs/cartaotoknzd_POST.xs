// Add CARTAOTOKNZD record
query cartaotoknzd verb=POST {
  api_group = "Event Logs"

  input {
    dblink {
      table = "CARTAOTOKNZD"
    }
  }

  stack {
    db.add CARTAOTOKNZD {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $cartaotoknzd
  }

  response = $cartaotoknzd
  guid = "09P0cBNHEiNWrO8eBqv98716yfM"
}