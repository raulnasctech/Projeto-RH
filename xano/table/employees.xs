table employees {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int users_id? {
      table = "users"
    }
  
    int departments_id? {
      table = "departments"
    }
  
    text job_title? filters=trim
    date? hire_date?
    decimal salary?
    text status? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["rh-system"]
  guid = "buvoT-0HSzXCJ_acd4hQL39nsbA"
}