// Edit Telegram record
query "telegram/{telegram_id}" verb=PATCH {
  api_group = "Telegram_restaurante"

  input {
    int telegram_id? filters=min:1
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
      field_value = $input.telegram_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $telegram
  }

  response = $telegram
  guid = "bgIT7h67BJGQP6t8fOAOewvWoIk"
}