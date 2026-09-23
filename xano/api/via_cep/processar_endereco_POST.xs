query processar_endereco verb=POST {
  api_group = "ViaCEP"

  input {
    text cep_cliente? filters=trim
    text user_id? filters=trim
  }

  stack {
    db.get CEP {
      field_name = "cep"
      field_value = $input.cep_cliente
    } as $CEP1
  
    conditional {
      if ($CEP1 == null) {
        api.request {
          url = ``
          method = "GET"
        } as $api1
      }
    }
  }

  response = $CEP1
  guid = "FfEycTsvv0mbodN6Lylwm49Kgio"
}