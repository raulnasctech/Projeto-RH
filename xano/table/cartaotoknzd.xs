// CARTAOTOKNZD
table CARTAOTOKNZD {
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
  
    // token
    text token? filters=trim
  
    // codigoclienteassas
    text codigoclienteassas? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["sabor local "]
  guid = "4jltl1mlUf7OsNCh0nA3palFDSk"
}