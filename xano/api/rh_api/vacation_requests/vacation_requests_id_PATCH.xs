// Edit vacation_requests record
query "vacation_requests/{vacation_requests_id}" verb=PATCH {
  api_group = "rh_api"

  input {
    int vacation_requests_id? filters=min:1
    dblink {
      table = "vacation_requests"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch vacation_requests {
      field_name = "id"
      field_value = $input.vacation_requests_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $vacation_requests
  }

  response = $vacation_requests
  guid = "TA_AXjgLT-tRtVFxdaY1MzmDhto"
}