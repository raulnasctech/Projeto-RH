// Add users record
query users verb=POST {
  api_group = "rh_api"

  input {
    dblink {
      table = "users"
    }
  }

  stack {
    db.add users {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $users
  }

  response = $users
  guid = "_LSHKlG9roqJkp8jBUHVMdCej6Y"
}