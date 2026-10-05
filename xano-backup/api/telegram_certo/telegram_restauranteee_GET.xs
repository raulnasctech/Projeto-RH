// Query all Telegram_Restauranteee records
query telegram_restauranteee verb=GET {
  api_group = "Telegram_certo"

  input {
  }

  stack {
    db.query "" {
      return = {type: "list"}
    } as $telegram_restauranteee
  }

  response = $telegram_restauranteee
  guid = "lXYUdL-0DZSq1DqhSBJ0VoD1tIk"
}