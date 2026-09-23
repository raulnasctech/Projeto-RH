// Delete FAQ record.
query "faq/{faq_id}" verb=DELETE {
  api_group = "Event Logs"

  input {
    int faq_id? filters=min:1
  }

  stack {
    db.del FAQ {
      field_name = "id"
      field_value = $input.faq_id
    }
  }

  response = null
  guid = "qLXdeHSll2BE3WCF38q186b11hI"
}