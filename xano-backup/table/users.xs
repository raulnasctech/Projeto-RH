table users {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text name? filters=trim
    email email filters=trim|lower
    password password {
      sensitive = true
      visibility = "internal"
    }
  
    text role? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["rh-system"]
  guid = "YzA-zbzpiEyuSl0YQaAuxvoY7vs"
}