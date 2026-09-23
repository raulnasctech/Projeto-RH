// Query all STATUS_ITEM records
query status_item verb=GET {
  api_group = "Event Logs"

  input {
  }

  stack {
    db.query STATUS_ITEM {
      return = {type: "list"}
    } as $status_item
  }

  response = $status_item
  guid = "DYdcWxvAZqinDugPmNKUSVx1cJk"
}