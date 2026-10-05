// Edit users record
query "users/{users_id}" verb=PATCH {
  api_group = "rh_api"

  input {
    int users_id? filters=min:1
    dblink {
      table = "users"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch users {
      field_name = "id"
      field_value = $input.users_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $users
  }

  response = $users
  guid = "oBc1h6KmGun0szqIaP_oaOzcG6U"
}