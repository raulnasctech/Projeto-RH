query consultacep verb=GET {
  api_group = "ViaCEP"

  input {
    text cep? filters=trim
  }

  stack {
    var $url {
      value = '"https://viacep.com.br/ws/" ~ $input.cep ~ "/json"'
    }
  
    api.request {
      url = `https://viacep.com.br/ws/{cep_cliente}/json`
      method = "GET"
    } as $api1
  
    db.add CEP {
      enforce_hidden_fields = false
      data = {
        cep   : $input.cep
        uf    : "x1.endereco.uf "
        cidade: "x1.endereco.localidade"
      }
    } as $CEP1
  
    var $x1 {
      value = "{ status: $var.api1.response.status, endereco: $var.api1.response.result }"
    }
  
    var $erro {
      value = true
    }
  
    try_catch {
      try {
        var $erro {
          value = $x1.endereco.erro
        }
      }
    
      catch {
        var $erro {
          value = false
        }
      }
    }
  
    conditional {
      if ($x1.status == 400 || $erro) {
        var $resp {
          value = '{"status": true, "endereco": $x1.endereco}'
        }
      }
    
      else {
        var $resp {
          value = '{"status": true, "endereco": $x1.endereco}'
        }
      }
    }
  }

  response = {"": $url, resp: $resp}
  guid = "Dn-TU3naXyXQ65aB2XRonBoIRDs"
}