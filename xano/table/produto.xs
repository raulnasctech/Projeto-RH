// PRODUTO
table PRODUTO {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // nome
    text nome? filters=trim
  
    // descricao
    text descricao? filters=trim
  
    // qtd_disp
    int qtd_disp?
  
    // url_imagem
    text url_imagem? filters=trim
  
    // preco
    decimal preco?
  
    // precisa_produzir?
    bool precisa_produzir?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["sabor local "]
  guid = "_PHm7dTtazHh-SJHryrMJhgIptE"
}