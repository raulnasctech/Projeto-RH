// Query all TTOKENIZACAO records
query ttokenizacao verb=GET {
  api_group = "Event Logs"

  input {
  }

  stack {
    db.query TTOKENIZACAO {
      return = {type: "list"}
    } as $ttokenizacao
  }

  response = $ttokenizacao
  guid = "HeTdwU2cfxfbgXQadsS43Mz03I0"
}