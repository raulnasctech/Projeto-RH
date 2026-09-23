// Edit tokens record
query "tokens/{tokens_id}" verb=PATCH {
  api_group = "Event Logs"

  input {
    int tokens_id? filters=min:1
    dblink {
      table = "tokens"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch tokens {
      field_name = "id"
      field_value = $input.tokens_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $tokens
  }

  response = $tokens
  guid = "083qazBI--4_jt1ZXdJIY8NTB4M"
}