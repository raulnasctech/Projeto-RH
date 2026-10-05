// Get CARTAOTOKNZD record
query "cartaotoknzd/{cartaotoknzd_id}" verb=GET {
  api_group = "Event Logs"

  input {
    int cartaotoknzd_id? filters=min:1
  }

  stack {
    db.get CARTAOTOKNZD {
      field_name = "id"
      field_value = $input.cartaotoknzd_id
    } as $cartaotoknzd
  
    precondition ($cartaotoknzd != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $cartaotoknzd
  guid = "oMUthKukK3BfVmJRaGxm_-KU4-g"
}