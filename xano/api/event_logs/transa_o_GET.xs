// Query all TRANSAÇÃO records
query transa_o verb=GET {
  api_group = "Event Logs"

  input {
  }

  stack {
    db.query "TRANSAÇÃO" {
      return = {type: "list"}
    } as $transa_o
  }

  response = $transa_o
  guid = "lyMqjl2Tppls611royp2iVPJRfI"
}