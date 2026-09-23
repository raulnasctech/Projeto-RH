query criarclienteassas_v2 verb=POST {
  api_group = "Assas"

  input {
    text authtoken filters=trim
    text tipo_cobranca filters=trim
    decimal valor
    text data_vencimento filters=trim
    text descricao? filters=trim
  }

  stack {
    api.request {
      url = "https://x8ki-letl-twmt.n7.xano.io/api:ddB1rUAm/auth/me"
      method = "GET"
      headers = ["Authorization: Bearer " ~ $input.authtoken]
    } as $auth_result
  
    // Define o usuário para uso posterior
    var $usuario {
      value = `$auth_result.response.result`
    }
  
    var $debug {
      value = $usuario
    }
  
    db.get tokens {
      field_name = "plataforma"
      field_value = "Assas"
    } as $token_assas
  
    var $asaas_token {
      value = $token_assas.token
    }
  
    db.get CARTAOTOKNZD {
      field_name = "cliente_id"
      field_value = `$usuario.id`
    } as $cartao_existente
  
    var $clienteassas_id {
      value = ""
    }
  
    conditional {
      if ($cartao_existente != null && $cartao_existente.codigoclienteassas != "") {
        var.update $clienteassas_id {
          value = `$cartao_existente.codigoclienteassas`
        }
      }
    
      else {
        db.get user {
          field_name = "id"
          field_value = `$usuario.id`
        } as $user_data
      
        api.request {
          url = "https://api-sandbox.asaas.com/v3/customers"
          method = "POST"
          params = ```
            {
              name                : `$user_data.name`
              email               : `$user_data.email`
              cpfCnpj             : "/[^0-9]/"|regex_replace:"":$user_data.cpf ?? ""
              mobilePhone         : `$user_data.celular`
              notificationDisabled: false
            }
            ```
          headers = [
            "access_token: " ~ $asaas_token
            "Content-Type: application/json"
            "Accept: application/json"
            "User-Agent: XanoScript"
          ]
        } as $criar_cliente
      
        precondition ($criar_cliente.response.status == 200 || $criar_cliente.response.status == 201) {
          error = "Erro ao criar cliente no Asaas: " ~ ($criar_cliente.response.result.errors.0.description|to_text)
        }
      
        var.update $clienteassas_id {
          value = `$criar_cliente.response.result.id`
        }
      
        db.add CARTAOTOKNZD {
          enforce_hidden_fields = false
          data = {
            cliente_id        : `$usuario.id`
            codigoclienteassas: `$clienteassas_id`
          }
        } as $novo_cartao
      
        db.get STATUS_TTOKENIZACAO {
          field_name = "status"
          field_value = "Criada"
        } as $status_token
      
        db.add TTOKENIZACAO {
          enforce_hidden_fields = false
          data = {
            cliente_id            : `$usuario.id`
            status_ttokenizacao_id: `$status_token.id`
          }
        } as $nova_tokenizacao
      }
    }
  
    var $descricao_final {
      value = "Cobrança SLFood"
    }
  
    conditional {
      if ($input.descricao != null && $input.descricao != "") {
        var.update $descricao_final {
          value = `$input.descricao`
        }
      }
    }
  
    api.request {
      url = "https://api-sandbox.asaas.com/v3/payments"
      method = "POST"
      params = {
        customer   : `$clienteassas_id`
        billingType: `$input.tipo_cobranca`
        value      : `$input.valor`
        dueDate    : `$input.data_vencimento`
        description: `$descricao_final`
      }
    
      headers = [
        "access_token: " ~ $asaas_token
        "Content-Type: application/json"
        "Accept: application/json"
        "User-Agent: XanoScript"
      ]
    } as $criar_cobranca
  
    precondition ($criar_cobranca.response.status == 200 || $criar_cobranca.response.status == 201) {
      error = "Erro ao criar cobrança no Asaas: " ~ ($criar_cobranca.response.result.errors.0.description|to_text)
    }
  
    db.get STATUS_TRANSACAO {
      field_name = "status"
      field_value = "Cobrança Criada"
    } as $status_cobr_criada
  
    db.add "TRANSAÇÃO" {
      enforce_hidden_fields = false
      data = {
        clienteassas       : `$clienteassas_id`
        idpayment          : `$criar_cobranca.response.result.id`
        tipo               : `$input.tipo_cobranca`
        valor              : `$input.valor`
        datavenc           : `$input.data_vencimento`
        descricao          : `$descricao_final`
        statustransacao_id : `$status_cobr_criada.id`
        pedido_id          : 0
        status_transacao_id: 0
      }
    } as $nova_transacao
  
    var $resposta {
      value = {
        status          : true
        mensagem        : "Cobrança criada com sucesso."
        cliente_assas_id: `$clienteassas_id`
        cobranca_id     : `$criar_cobranca.response.result.id`
        tipo            : `$input.tipo_cobranca`
        valor           : `$input.valor`
        vencimento      : `$input.data_vencimento`
        pix_payload     : `$criar_cobranca.response.result.pixQrCode.payload`
        pix_qrcode      : `$criar_cobranca.response.result.pixQrCode.encodedImage`
        boleto_linha    : `$criar_cobranca.response.result.bankSlipUrl`
        boleto_url      : `$criar_cobranca.response.result.invoiceUrl`
      }
    }
  }

  response = $debug
  guid = "fzNDqPADmGGbcKiHIvsNUkw7c9o"
}