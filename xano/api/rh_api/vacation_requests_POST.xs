// Add vacation_requests record
query vacation_requests verb=POST {
  api_group = "rh_api"

  input {
    dblink {
      table = "vacation_requests"
    }
  }

  stack {
    db.add vacation_requests {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $vacation_requests
  }

  response = $vacation_requests
  guid = "PhMK_KSKsG-cjGbkYIZpzAJ9ZsU"
}