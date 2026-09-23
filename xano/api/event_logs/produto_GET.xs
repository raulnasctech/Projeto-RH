// Query all PRODUTO records
query produto verb=GET {
  api_group = "Event Logs"

  input {
  }

  stack {
    db.query PRODUTO {
      return = {type: "list"}
    } as $produto
  }

  response = $produto
  guid = "uArZo7ygGlUlk5hDe-nKIg2jZvE"
}