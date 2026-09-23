// Add departments record
query departments verb=POST {
  api_group = "rh_api"

  input {
    dblink {
      table = "departments"
    }
  }

  stack {
    db.add departments {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $departments
  }

  response = $departments
  guid = "wMw7WYJAPBzLFTh68hqJTeJHL0w"
}