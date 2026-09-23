// Query all OE records
query oe verb=GET {
  api_group = "Event Logs"

  input {
  }

  stack {
    db.query OE {
      return = {type: "list"}
    } as $oe
  }

  response = $oe
  guid = "b5PeTXUWYW0aNgKXF28OFuztlCg"
}