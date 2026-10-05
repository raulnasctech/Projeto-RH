// CEP
table CEP {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // cep
    text cep? filters=trim
  
    // uf
    text uf? filters=trim
  
    // cidade
    text cidade? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["sabor local "]
  guid = "-R1PZd2QTXWAyBuiBho16-sxRZo"
}