// Add FAQ record
query faq verb=POST {
  api_group = "Event Logs"

  input {
    dblink {
      table = "FAQ"
    }
  }

  stack {
    db.add FAQ {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $faq
  }

  response = $faq
  guid = "lWi__RVymi8E5Yqccrp9DkYZNsc"
}