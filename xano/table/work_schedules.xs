table work_schedules {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }

    int employees_id {
      table = "employees"
    }

    json weekly_schedule
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {
      type : "btree|unique"
      field: [{name: "employees_id", op: "asc"}]
    }
  ]

  tags = ["rh-system"]
  guid = "Ufu5GM5Dz0FAtjcAW8I9Jwhnt-4"
}
