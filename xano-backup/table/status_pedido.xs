// STATUS do PEDIDO
table STATUS_PEDIDO {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // status
    text status? filters=trim
  
    // status para
    text status_para? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["sabor local "]
  guid = "3ngKvcu_PDppEI1EHrX_XPotHX0"
}