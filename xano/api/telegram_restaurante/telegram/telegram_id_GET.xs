// Get Telegram record
query "telegram/{telegram_id}" verb=GET {
  api_group = "Telegram_restaurante"

  input {
    int telegram_id? filters=min:1
  }

  stack {
    db.get "" {
      field_name = "id"
      field_value = $input.telegram_id
    } as $telegram
  
    precondition ($telegram != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $telegram
  guid = "4izAJ0B8eEo5GdSiCI7kM-q1C_I"
}