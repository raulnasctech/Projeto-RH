// Add STATUS_ITEM record
query status_item verb=POST {
  api_group = "Event Logs"

  input {
    dblink {
      table = "STATUS_ITEM"
    }
  }

  stack {
    db.add STATUS_ITEM {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $status_item
  }

  response = $status_item
  guid = "4zSTX4NnfJ966fl89GZsZ5aY4Nc"
}