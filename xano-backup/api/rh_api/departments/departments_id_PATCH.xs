// Edit departments record
query "departments/{departments_id}" verb=PATCH {
  api_group = "rh_api"

  input {
    int departments_id? filters=min:1
    dblink {
      table = "departments"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch departments {
      field_name = "id"
      field_value = $input.departments_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $departments
  }

  response = $departments
  guid = "X3gTRFgiE_k6oe4z5XYaafHY4co"
}