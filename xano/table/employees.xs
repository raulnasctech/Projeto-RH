table employees {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int user_id? {
      table = "user"
    }

    text name? filters=trim

    int departaments_id? {
      table = "departaments"
    }
  
    text job_title? filters=trim
    date? admissao?
    decimal salario?
    text status? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "77PCRmEyKGAHbXE-SCjbpIfUrDc"
}
