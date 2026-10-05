// Add tokens record
query tokens verb=POST {
  api_group = "Event Logs"

  input {
    dblink {
      table = "tokens"
    }
  }

  stack {
    db.add tokens {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $tokens
  }

  response = $tokens
  guid = "MmggdcQGZOZAV044nUjN16Jv340"
}