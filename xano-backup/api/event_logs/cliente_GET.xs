// Query all CLIENTE records
query cliente verb=GET {
  api_group = "Event Logs"

  input {
  }

  stack {
    db.query CLIENTE {
      return = {type: "list"}
    } as $cliente
  }

  response = $cliente
  guid = "lS7G3MvhryOt9DuDSxaO4G4J94w"
}