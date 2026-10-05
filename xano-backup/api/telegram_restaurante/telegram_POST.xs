// Add Telegram record
query telegram verb=POST {
  api_group = "Telegram_restaurante"

  input {
    dblink {
      table = ""
    }
  }

  stack {
    db.add "" {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $telegram
  }

  response = $telegram
  guid = "etDhCU_l3zaBevabdcKM8QROkm4"
}