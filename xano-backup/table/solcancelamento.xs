// SOLCANCELAMENTO
table SOLCANCELAMENTO {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // motivo
    text motivo? filters=trim
  
    // referencia 
    int pedido_id? {
      table = "PEDIDO"
    }
  
    // referencia 
    int status_solcancelamento_id? {
      table = "STATUS_SOLCANCELAMENTO"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["sabor local "]
  guid = "TL-u49soRBqTiLh466xDHR_pI78"
}