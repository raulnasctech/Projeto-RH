// transação 
table "TRANSAÇÃO" {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // clienteassas
    text clienteassas? filters=trim
  
    // idpayment
    text idpayment? filters=trim
  
    // tipo
    text tipo? filters=trim
  
    // valor
    decimal valor?
  
    // datavenc
    text datavenc? filters=trim
  
    // descricao
    text descricao? filters=trim
  
    // id do statustransacao
    int statustransacao_id?
  
    int pedido_id?
    int status_transacao_id?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["sabor local "]
  guid = "GdxCimJLgKsQ6-3mF5mknZWbBM0"
}