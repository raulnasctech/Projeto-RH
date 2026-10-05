// OE
table OE {
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
    int status_oe_id? {
      table = "STATUS_OE"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["sabor local "]
  guid = "LF3f_uroGUsBXDr4pwjOGG16RyE"
}