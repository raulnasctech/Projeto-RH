// Add employees record
query employees verb=POST {
  api_group = "rh_api"

  input {
    dblink {
      table = "employees"
    }
  }

  stack {
    db.add employees {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $employees
  }

  response = $employees
  guid = "uYojWHLYm6YypAl-0IYbC2EZPXk"
}