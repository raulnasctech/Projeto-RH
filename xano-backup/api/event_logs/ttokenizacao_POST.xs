// Add TTOKENIZACAO record
query ttokenizacao verb=POST {
  api_group = "Event Logs"

  input {
    dblink {
      table = "TTOKENIZACAO"
    }
  }

  stack {
    db.add TTOKENIZACAO {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $ttokenizacao
  }

  response = $ttokenizacao
  guid = "Eb2E76pkOtmYB4IDnW6QoFu6BkM"
}