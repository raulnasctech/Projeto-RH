// Query all tokens records
query tokens verb=GET {
  api_group = "Event Logs"

  input {
  }

  stack {
    db.query tokens {
      return = {type: "list"}
    } as $tokens
  }

  response = $tokens
  guid = "U2BeZ1nfJndl-LCF014S6efnjBg"
}