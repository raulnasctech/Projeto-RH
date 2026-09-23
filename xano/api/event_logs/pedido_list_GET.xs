// Query all PEDIDO records
query pedidoList verb=GET {
  api_group = "Event Logs"

  input {
  }

  stack {
    db.query PEDIDO {
      return = {type: "list"}
    } as $model
  }

  response = $model
  guid = "EgkftKiqQ5dI15oDrBrizXCv2ZM"
}