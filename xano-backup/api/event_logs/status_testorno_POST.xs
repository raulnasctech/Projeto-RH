// Add STATUS_TESTORNO record
query status_testorno verb=POST {
  api_group = "Event Logs"

  input {
    dblink {
      table = "STATUS_TESTORNO"
    }
  }

  stack {
    db.add STATUS_TESTORNO {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $status_testorno
  }

  response = $status_testorno
  guid = "Wz98xrz6da84Ox38bqPZhZ21S5A"
}