// Query all PAPEL records
query papel verb=GET {
  api_group = "Event Logs"

  input {
  }

  stack {
    db.query PAPEL {
      return = {type: "list"}
    } as $papel
  }

  response = $papel
  guid = "c8mjr1fkhstpRUD8cyfHqtFUoRU"
}