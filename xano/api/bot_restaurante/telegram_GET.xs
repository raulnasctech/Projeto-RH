// Query all Telegram records
query telegram verb=GET {
  api_group = "Bot_Restaurante"

  input {
  }

  stack {
    db.query "" {
      return = {type: "list"}
    } as $telegram
  }

  response = $telegram
  guid = "eQMlfLQ5urYPgrkMZN-06iidyNc"
}