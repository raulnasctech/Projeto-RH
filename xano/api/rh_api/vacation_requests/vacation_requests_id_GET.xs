// Get vacation_requests record
query "vacation_requests/{vacation_requests_id}" verb=GET {
  api_group = "rh_api"

  input {
    int vacation_requests_id? filters=min:1
  }

  stack {
    db.get vacation_requests {
      field_name = "id"
      field_value = $input.vacation_requests_id
    } as $vacation_requests
  
    precondition ($vacation_requests != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $vacation_requests
  guid = "WkbTagz1QgKAn3qXDX2UTuRBj3Y"
}