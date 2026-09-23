// FAQ
table FAQ {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // pergunta
    text pergunta? filters=trim
  
    // resposta
    text resposta? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["sabor local "]
  guid = "eXeYlOl13XwFVIXZNeHP1alZgxA"
}