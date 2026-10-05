// Delete departments record.
query "departments/{departments_id}" verb=DELETE {
  api_group = "rh_api"

  input {
    int departments_id? filters=min:1
  }

  stack {
    db.del departments {
      field_name = "id"
      field_value = $input.departments_id
    }
  }

  response = null
  guid = "Pepp-tX_3yw9A_WOvNxeWt95Sfk"
}