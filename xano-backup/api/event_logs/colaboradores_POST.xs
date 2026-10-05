// Add Colaboradores record
query colaboradores verb=POST {
  api_group = "Event Logs"

  input {
    dblink {
      table = "Colaboradores"
    }
  }

  stack {
    db.add Colaboradores {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $colaboradores
  }

  response = $colaboradores
  guid = "rrokgtdtiM3NgbB_Dz9JYJw5RlI"
}