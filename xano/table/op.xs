// OP
table OP {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // referencia 
    int pedido_id? {
      table = "PEDIDO"
    }
  
    // referencia 
    int status_op_id? {
      table = "STATUS_OP"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["sabor local "]
  guid = "-AiTBjptXS95bj1sMRfK3au52k4"
}