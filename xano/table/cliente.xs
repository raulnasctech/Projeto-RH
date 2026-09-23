// CLIENTE
table CLIENTE {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // referencia 
    int user_id? {
      table = "user"
    }
  
    // celular
    text celular? filters=trim
  
    // cpf
    text cpf? filters=trim
  
    // referencia 
    int status_cliente_id? {
      table = "STATUS_CLIENTE"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["sabor local "]
  guid = "R6Wy0hfaTvE69zyG-vbSrkcPQM8"
}