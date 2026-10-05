query get_todos_produtos verb=GET {
  api_group = "Produtos"

  input {
  }

  stack {
    db.query PRODUTO {
      return = {type: "list"}
    } as $PRODUTO1
  }

  response = {PRODUTO12: $PRODUTO1, PRODUTO1: $PRODUTO1}
  guid = "tVnOwtUh8whU3Xd2OeNsQ9-roAA"
}