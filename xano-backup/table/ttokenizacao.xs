// TTOKENIZACAO
table TTOKENIZACAO {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // referencia 
    int cliente_id? {
      table = "CLIENTE"
    }
  
    // det_cartao_encript
    text det_cartao_encript? filters=trim
  
    // referencia 
    int status_ttokenizacao_id? {
      table = "STATUS_TTOKENIZACAO"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["sabor local "]
  guid = "3GnvavVnqbgjAAclS-JAwH4z3XI"
}