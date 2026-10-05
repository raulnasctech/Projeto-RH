// Query all employees records
query employees verb=GET {
  api_group = "rh_api"

  input {
  }

  stack {
    db.query employees {
      return = {type: "list"}
    } as $employees
  }

  response = $employees
  guid = "xWRaXUKGQM0DGRv15cDK2wgZH00"
}