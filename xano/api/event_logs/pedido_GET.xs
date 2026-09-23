// Query all PEDIDO records
query pedido verb=GET {
  api_group = "Event Logs"
  auth = "user"

  input {
  }

  stack {
    db.query PEDIDO {
      return = {type: "list"}
    } as $pedido
  }

  response = $pedido
  guid = "k3fgzmnwAEvF6_awuDP2v0hbxMk"
}