// Add Telegram record
query telegram verb=POST {
  api_group = "Bot_Restaurante"

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
  guid = "3Lw1nPkzuEUcaselrjxCCbsF9PA"
}