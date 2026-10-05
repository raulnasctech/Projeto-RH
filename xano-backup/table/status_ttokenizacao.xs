// STATUS da  TTOKENIZACAO
table STATUS_TTOKENIZACAO {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // status da tokenlixação 
    text status? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["sabor local "]
  guid = "jdgq1mlx-ON1XSsMt0qCuQBDqmo"
}