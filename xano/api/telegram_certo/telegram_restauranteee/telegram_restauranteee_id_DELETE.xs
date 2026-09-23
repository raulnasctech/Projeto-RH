// Delete Telegram_Restauranteee record.
query "telegram_restauranteee/{telegram_restauranteee_id}" verb=DELETE {
  api_group = "Telegram_certo"

  input {
    int telegram_restauranteee_id? filters=min:1
  }

  stack {
    db.del "" {
      field_name = "id"
      field_value = $input.telegram_restauranteee_id
    }
  }

  response = null
  guid = "55AHbl3Vfht0xuUvP40QotM_1Gw"
}