// Edit Telegram_Restauranteee record
query "telegram_restauranteee/{telegram_restauranteee_id}" verb=PATCH {
  api_group = "Telegram_certo"

  input {
    int telegram_restauranteee_id? filters=min:1
    dblink {
      table = ""
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch "" {
      field_name = "id"
      field_value = $input.telegram_restauranteee_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $telegram_restauranteee
  }

  response = $telegram_restauranteee
  guid = "LKy4gig0TljpGVO_5Oil8_pWH84"
}