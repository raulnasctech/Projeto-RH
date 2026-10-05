query criarclienteassas verb=POST {
  api_group = "Assas"

  input {
    text authtoken? filters=trim
    text user_id? filters=trim
  }

  stack {
    api.request {
      url = "If $var.api1.response.result.erro == false"
      method = "GET"
      params = '{"authtoken": $input.authtoken}'
    } as $api1
  
    conditional {
      if ("$var.api1.response.result.erro" == false) {
        db.get user {
          field_name = "id"
          field_value = `$var.api1.response.result.cliente.user_id`
        } as $user1
      
        db.get tokens {
          field_name = "plataforma"
          field_value = "Assas"
        } as $tokens1
      
        api.request {
          url = "https://api-sandbox.asaas.com/v3/customers"
          method = "POST"
          params = ```
            access_token
            REPLACE_WITH_ASAAS_API_TOKEN
            ```
          headers = [
            $tokens1.token
            "Content-Type: application/json"
            "Accept: application/json"
            "User-Agent: curl/8.0.1"
          ]
        
        } as $api2
      
        var $codigoclienteassas {
          value = `$var.api2.response.result.id`
        }
      
        db.get STATUS_TTOKENIZACAO {
          field_name = "status"
          field_value = "Criada"
        } as $STATUS_TTOKENIZACAO1
      
        db.add TTOKENIZACAO {
          enforce_hidden_fields = false
          data = {
            cliente_id            : `$var.api1.response.result.cliente.id`
            status_ttokenizacao_id: `$var.STATUS_TTOKENIZACAO1.id`
          }
        } as $STATUS_TTOKENIZACAO1
      
        db.add CARTAOTOKNZD {
          enforce_hidden_fields = false
          data = {
            cliente_id        : `$var.api1.response.result.cliente.id`
            codigoclienteassas: `$var.codigoclienteassas`
          }
        } as $CARTAOTOKNZD1
      
        var $status {
          value = {status: true, mensagem: "Cliente cadastrado no Assas."}
        }
      }
    
      else {
        var $status {
          value = {
            status  : false
            mensagem: "Cliente não pode ser cadastrado no Assas."
          }
        }
      }
    }
  
    db.get user {
      field_name = "id"
      field_value = $input.user_id
    } as $user2
  
    api.request {
      url = "https://api-sandbox.asaas.com/v3/customers"
      method = "POST"
    } as $api3
  }

  response = {api1: $api1, s: $status}
  guid = "qT5lcE3--XoKAMeNviJCHvqHv8A"
}