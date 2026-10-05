// ITEM
table ITEM {
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
  
    // qtd
    int qtd?
  
    // valor_unit
    decimal valor_unit?
  
    // subtotal
    decimal subtotal?
  
    // referencia
    int produto_id? {
      table = "PRODUTO"
    }
  
    // referencia 
    int status_item_id? {
      table = "STATUS_ITEM"
    }
  
    int item_pedido_id? {
      table = "PEDIDO"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["sabor local "]
  guid = "3CXKLTYOP7Y7nKdd0AI9SR0dNko"
}