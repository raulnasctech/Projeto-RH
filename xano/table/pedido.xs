// PEDIDO
table PEDIDO {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // total
    decimal total?
  
    // nfc_e
    text nfc_e? filters=trim
  
    // cod_entrega
    text cod_entrega? filters=trim
  
    // referencia 
    int cliente_id? {
      table = "CLIENTE"
    }
  
    // referencia
    int status_pedido_id? {
      table = "STATUS_PEDIDO"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["sabor local "]
  guid = "QINpBs6VJtuDkn-9tacM7tfXhPk"
}