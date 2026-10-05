// ════════════════════════════════════════════════════════════════════════════
// ENDPOINT 2 — tokenizarcartao
// ════════════════════════════════════════════════════════════════════════════
query tokenizarcartao verb=POST {
  api_group = "AASSAS"

  input {
    // Token de autenticação do usuário (JWT do Xano)
    text authtoken filters=trim
  
    // Nome impresso no cartão
    text holdername filters=trim
  
    // Número do cartão
    text number filters=trim
  
    // Mês de expiração (MM)
    text expirymonth filters=trim
  
    // Ano de expiração (AAAA)
    text expiryyear filters=trim
  
    // Código de segurança (CCV)
    text ccv filters=trim
  
    // CEP do titular
    text postalcode filters=trim
  
    // Número do endereço
    text addressnumber filters=trim
  
    // Telefone do titular
    text phone filters=trim
  }

  stack {
    // 1. Valida o authtoken enviado no input via chamada interna ao endpoint /auth/me
    api.request {
      url = "https://x8ki-letl-twmt.n7.xano.io/api:ddB1rUAm/auth/me"
      method = "GET"
      headers = ["Authorization: Bearer " ~ $input.authtoken]
    } as $auth_result
  
    precondition ($auth_result.response.status == 200) {
      error = "Token inválido ou expirado. Faça login novamente."
    }
  
    // 2. Busca o registro completo do usuário no banco para garantir o codigoclienteassas atualizado
    db.get user {
      field_name = "id"
      field_value = $auth_result.response.result.id
    } as $user_record
  
    precondition ($user_record != null) {
      error = "Usuário não localizado no banco de dados."
    }
  
    // Valida se o usuário possui o código de cliente do Asaas preenchido (requisito do usuário)
    precondition (($user_record.customer_id_asaas ?? "") != "") {
      error = "Erro ao tokenizar cartão: Cliente inválido ou não informado no cadastro do usuário."
    }
  
    // 3. Busca o registro na tabela CLIENTE vinculado a este usuário
    db.get CLIENTE {
      field_name = "user_id"
      field_value = $user_record.id
    } as $cliente
  
    precondition ($cliente != null) {
      error = "Cliente não encontrado para este usuário na tabela CLIENTE."
    }
  
    // 4. Busca o registro de cartão tokenizado (CARTAOTOKNZD) para este cliente
    db.query CARTAOTOKNZD {
      where = $db.CARTAOTOKNZD.cliente_id == $cliente.id
      sort = {id: "desc"}
      return = {type: "single"}
    } as $cartaotoknzd_record
  
    // Se não existir, criamos um registro base para armazenar o token futuramente
    conditional {
      if ($cartaotoknzd_record == null) {
        db.add CARTAOTOKNZD {
          enforce_hidden_fields = false
          data = {
            cliente_id        : $cliente.id
            codigoclienteassas: $user_record.customer_id_asaas
          }
        } as $cartaotoknzd_record
      }
    }
  
    // 5. Busca o token de API do Asaas na tabela de configurações
    db.get tokens {
      field_name = "plataforma"
      field_value = "Assas"
    } as $asaas_config
  
    precondition ($asaas_config != null) {
      error = "Token do Asaas não configurado na tabela tokens."
    }
  
    // Prepara o header de autorização (access_token: ...)
    var $final_token_header {
      value = $asaas_config.token
    }
  
    conditional {
      if (($asaas_config.token|istarts_with:"access_token:") == false) {
        var.update $final_token_header {
          value = "access_token: " ~ $asaas_config.token
        }
      }
    }
  
    // Limpa caracteres não numéricos do CPF do usuário
    var $cpf_limpo {
      value = "/[^0-9]/"
        |regex_replace:"":$user_record.cpf ?? ""
    }
  
    // 6. Chama a API do Asaas para tokenizar o cartão usando o codigoclienteassas do usuário
    api.request {
      url = "https://api-sandbox.asaas.com/v3/creditCard/tokenize"
      method = "POST"
      params = {
        customer            : $user_record.customer_id_asaas
        creditCard          : {
          holderName: $input.holdername,
          number: $input.number,
          expiryMonth: $input.expirymonth,
          expiryYear: $input.expiryyear,
          ccv: $input.ccv
        }
        creditCardHolderInfo: {
          name: $user_record.name,
          email: $user_record.email,
          cpfCnpj: $cpf_limpo,
          postalCode: $input.postalcode,
          addressNumber: $input.addressnumber,
          phone: $input.phone
        }
      }
    
      headers = [
        $final_token_header
        "Content-Type: application/json"
        "Accept: application/json"
        "User-Agent: IntegracaoXano"
      ]
    } as $api_tokenize
  
    // Validação da resposta da API do Asaas
    precondition ($api_tokenize.response.status == 200 || $api_tokenize.response.status == 201) {
      error = "Erro ao tokenizar cartão: " ~ ($api_tokenize.response.result.errors.0.description|to_text)
    }
  
    // 7. Atualiza o registro CARTAOTOKNZD com o token retornado
    db.edit CARTAOTOKNZD {
      field_name = "id"
      field_value = $cartaotoknzd_record.id
      enforce_hidden_fields = false
      data = {
        token             : $api_tokenize.response.result.creditCardToken
        codigoclienteassas: $user_record.customer_id_asaas
      }
    }
  
    // 8. Localiza e atualiza o status do processo na tabela TTOKENIZACAO
    db.get STATUS_TTOKENIZACAO {
      field_name = "status"
      field_value = "Finalizada"
    } as $status_finalizada
  
    db.query TTOKENIZACAO {
      where = $db.TTOKENIZACAO.cliente_id == $cliente.id
      sort = {id: "desc"}
      return = {type: "single"}
    } as $tokenizacao_history
  
    conditional {
      if ($tokenizacao_history != null) {
        db.edit TTOKENIZACAO {
          field_name = "id"
          field_value = $tokenizacao_history.id
          enforce_hidden_fields = false
          data = {status_ttokenizacao_id: $status_finalizada.id}
        }
      }
    }
  
    // 9. Resposta de sucesso para o cliente
    var $final_status {
      value = {
        status  : true
        mensagem: "Cartão tokenizado com sucesso."
        token   : $api_tokenize.response.result.creditCardToken
      }
    }
  }

  response = $final_status
  guid = "xoEGam0VJi8VeTiNvSX1h4Nz-MY"
}