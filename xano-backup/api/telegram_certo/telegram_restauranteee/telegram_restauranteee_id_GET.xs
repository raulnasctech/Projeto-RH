// Get Telegram_Restauranteee record
query "telegram_restauranteee/{telegram_restauranteee_id}" verb=GET {
  api_group = "Telegram_certo"

  input {
    int telegram_restauranteee_id? filters=min:1
  }

  stack {
    db.get "" {
      field_name = "id"
      field_value = $input.telegram_restauranteee_id
    } as $telegram_restauranteee
  
    precondition ($telegram_restauranteee != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $telegram_restauranteee
  guid = "FiF2E0tGQs6DUvbr2vnY16HrTB4"
}