// Delete vacation_requests record.
query "vacation_requests/{vacation_requests_id}" verb=DELETE {
  api_group = "rh_api"

  input {
    int vacation_requests_id? filters=min:1
  }

  stack {
    db.del vacation_requests {
      field_name = "id"
      field_value = $input.vacation_requests_id
    }
  }

  response = null
  guid = "tQAu7HqSRi_24fGh4d0rBlNfRzg"
}