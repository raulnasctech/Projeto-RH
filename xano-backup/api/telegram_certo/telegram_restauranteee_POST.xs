// Add Telegram_Restauranteee record
query telegram_restauranteee verb=POST {
  api_group = "Telegram_certo"

  input {
    dblink {
      table = ""
    }
  }

  stack {
    db.add "" {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $telegram_restauranteee
  }

  response = $telegram_restauranteee
  guid = "cXCXGB59hJfgMNOs0jZqEd-M3Rs"
}