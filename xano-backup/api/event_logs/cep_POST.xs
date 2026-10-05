// Add CEP record
query cep verb=POST {
  api_group = "Event Logs"

  input {
    dblink {
      table = "CEP"
    }
  }

  stack {
    db.add CEP {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $cep
  }

  response = $cep
  guid = "jS-51jTZV8t-pXLGeH2HqV7Iozs"
}