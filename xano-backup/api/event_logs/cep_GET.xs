// Query all CEP records
query cep verb=GET {
  api_group = "Event Logs"

  input {
  }

  stack {
    db.query CEP {
      return = {type: "list"}
    } as $cep
  }

  response = $cep
  guid = "hRAK9xHGPvPHA4g_Wl-vZGvRUac"
}