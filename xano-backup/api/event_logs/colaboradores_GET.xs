// Query all Colaboradores records
query colaboradores verb=GET {
  api_group = "Event Logs"

  input {
  }

  stack {
    db.query Colaboradores {
      return = {type: "list"}
    } as $colaboradores
  }

  response = $colaboradores
  guid = "iwGtC-Wott6xeUGK8Lvt6OlGmiI"
}