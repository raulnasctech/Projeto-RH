// Immutable punch events for each employee's operational work day
table attendance_punches {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }

    int employees_id {
      table = "employees"
    }

    date work_date
    text punch_type filters=trim
    timestamp punched_at?=now
    json? schedule_snapshot?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {
      type : "btree|unique"
      field: [
        {name: "employees_id", op: "asc"}
        {name: "work_date", op: "asc"}
        {name: "punch_type", op: "asc"}
      ]
    }
    {type: "btree", field: [{name: "work_date", op: "asc"}]}
  ]

  tags = ["rh-system"]
  guid = "9BsfuunsmsQhIhLqz_baMpO0akw"
}
