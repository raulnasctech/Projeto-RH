// Add OE record
query oe verb=POST {
  api_group = "Event Logs"

  input {
    dblink {
      table = "OE"
    }
  }

  stack {
    db.add OE {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $oe
  }

  response = $oe
  guid = "axK9TEHiOrE9igHty6pG7PAxpv8"
}