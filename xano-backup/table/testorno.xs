// TESTORNO
table TESTORNO {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // valor
    decimal valor?
  
    // referencia 
    int solcancelamento_id? {
      table = "SOLCANCELAMENTO"
    }
  
    // referencia 
    int status_testorno_id? {
      table = "STATUS_TESTORNO"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["sabor local "]
  guid = "DHunCkZL2vVy3nodgFv_z1pi6yY"
}