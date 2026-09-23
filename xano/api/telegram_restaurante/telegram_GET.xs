// Query all Telegram records
query telegram verb=GET {
  api_group = "Telegram_restaurante"

  input {
  }

  stack {
    db.query "" {
      return = {type: "list"}
    } as $telegram
  }

  response = $telegram
  guid = "xMxV6YBFTBzx7JynVgarVjRXmBA"
}