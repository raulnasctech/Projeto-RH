// Get STATUS_ITEM record
query "status_item/{status_item_id}" verb=GET {
  api_group = "Event Logs"

  input {
    int status_item_id? filters=min:1
  }

  stack {
    db.get STATUS_ITEM {
      field_name = "id"
      field_value = $input.status_item_id
    } as $status_item
  
    precondition ($status_item != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $status_item
  guid = "ORVOOmnfoqPEbykYdXTlyIK0Cho"
}