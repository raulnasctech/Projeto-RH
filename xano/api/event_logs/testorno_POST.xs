// Add TESTORNO record
query testorno verb=POST {
  api_group = "Event Logs"

  input {
    dblink {
      table = "TESTORNO"
    }
  }

  stack {
    db.add TESTORNO {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $testorno
  }

  response = $testorno
  guid = "cifmKDD_o13FJJ81t9Gj-rUvGFo"
}