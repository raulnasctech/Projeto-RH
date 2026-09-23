addon PRODUTO {
  input {
    int PRODUTO_id? {
      table = "PRODUTO"
    }
  }

  stack {
    db.query PRODUTO {
      where = $db.PRODUTO.id == $input.PRODUTO_id
      return = {type: "list"}
    }
  }

  guid = "hWd8s5yYx3NdpxGl8-8_yZXu0BI"
}