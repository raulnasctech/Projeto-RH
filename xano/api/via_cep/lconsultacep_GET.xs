query lconsultacep verb=GET {
  api_group = "ViaCEP"

  input {
    text cep? filters=trim
  }

  stack {
    api.request {
      url = '"https://viacep.com.br/ws/" ~ $input.cep ~ "/json"'
      method = "GET"
    } as $api1
  
    var $resp {
      value = $api1
    }
  }

  response = {api1: $api1, resp: $resp}
  guid = "K-z2AxghB0giXAOxVq3iG0i6aGo"
}