// Query all TESTORNO records
query testorno verb=GET {
  api_group = "Event Logs"

  input {
  }

  stack {
    db.query TESTORNO {
      return = {type: "list"}
    } as $testorno
  }

  response = $testorno
  guid = "8fT_-AVZMJpfNxQslxuhhdDc6yw"
}