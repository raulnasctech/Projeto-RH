// Query all FAQ records
query faq verb=GET {
  api_group = "Event Logs"

  input {
  }

  stack {
    db.query FAQ {
      return = {type: "list"}
    } as $faq
  }

  response = $faq
  guid = "CnImYxAluKFfJVD547P33V5QKuk"
}