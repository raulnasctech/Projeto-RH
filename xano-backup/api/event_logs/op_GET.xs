// Query all OP records
query op verb=GET {
  api_group = "Event Logs"

  input {
  }

  stack {
    db.query OP {
      return = {type: "list"}
    } as $op
  }

  response = $op
  guid = "H_pgdtMqOTUC0t_zQuhYF2VyYDE"
}