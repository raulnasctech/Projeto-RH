// Delete Telegram record.
query "telegram/{telegram_id}" verb=DELETE {
  api_group = "Bot_Restaurante"

  input {
    int telegram_id? filters=min:1
  }

  stack {
    db.del "" {
      field_name = "id"
      field_value = $input.telegram_id
    }
  }

  response = null
  guid = "m-PHFs2P4vxUO3w0OgnDqh-Cmws"
}