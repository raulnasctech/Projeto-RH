table vacation_requests {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }

    int employees_id {
      table = "employees"
    }

    date start_date
    date end_date
    text status filters=trim

    int decided_by? {
      table = "user"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["rh-system"]
  guid = "KNRvKi1FemNc5fQu-zHQmYn9PTo"
}
