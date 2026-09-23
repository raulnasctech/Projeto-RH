// tokens
table tokens {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // plataforma
    text plataforma? filters=trim
  
    // token
    text token? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["sabor local "]
  guid = "2P78PG7sdPHsUFoM485FT1tQM74"
}