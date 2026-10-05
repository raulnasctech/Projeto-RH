// Query all PRODUTO records
query produto verb=GET {
  api_group = "produtos"

  input {
  }

  stack {
    db.query PRODUTO {
      where = $db.PRODUTO.nome ilike? "%search%"
      return = {type: "list"}
    } as $model
  }

  response = $model
  guid = "DvVsXlF939Tj6UhwnEkwW96lRvM"
}