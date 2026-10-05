// Query all CARTAOTOKNZD records
query cartaotoknzd verb=GET {
  api_group = "Event Logs"

  input {
  }

  stack {
    db.query CARTAOTOKNZD {
      return = {type: "list"}
    } as $cartaotoknzd
  }

  response = $cartaotoknzd
  guid = "6glkhGb87W4Kj2kO-0FjgBsee-8"
}