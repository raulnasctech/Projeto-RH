// ════════════════════════════════════════════════════════════════════════════
// ENDPOINT 4 — pagarcob
// Paga a cobrança com o token do cartão salvo
// Inputs: authtoken, transacao_id (ID do registro na tabela TRANSAÇÃO)
// ════════════════════════════════════════════════════════════════════════════
query pagarcob verb=POST {
  api_group = "AASSAS"

  input {
    text authtoken filters=trim
    int transacao_id
  }

  stack {
    // 1. Busca o usuário logado
    api.request {
      url = "https://x8ki-letl-twmt.n7.xano.io/api:ddB1rUAm/auth/me"
      method = "GET"
      headers = ["Authorization: Bearer " ~ $input.authtoken]
    } as $auth_result
  
    precondition ($auth_result.response.status == 200) {
      error = "Token inválido ou expirado. Faça login novamente."
    }
  
    var $usuario {
      value = `$auth_result.response.result`
    }
  
    // 2. Busca a transação pelo ID
    db.get "TRANSAÇÃO" {
      field_name = "id"
      field_value = `$input.transacao_id`
    } as $transacao1
  
    precondition ($transacao1 != null) {
      error = "Transação não encontrada."
    }
  
    // 3. Busca o CLIENTE
    db.get CLIENTE {
      field_name = "user_id"
      field_value = `$usuario.id`
    } as $cliente
  
    // 4. Busca o token do cartão
    db.get CARTAOTOKNZD {
      field_name = "cliente_id"
      field_value = `$cliente.id`
    } as $CARTAOTOKNZD1
  
    precondition ($CARTAOTOKNZD1 != null && $CARTAOTOKNZD1.token != "") {
      error = "Token do cartão não encontrado. Rode tokenizarcartao primeiro."
    }
  
    // 5. Busca o token do Asaas
    db.get tokens {
      field_name = "plataforma"
      field_value = "Assas"
    } as $tokens1
  
    precondition ($tokens1 != null) {
      error = "Token do Asaas não configurado na tabela tokens."
    }
  
    // Garante que o header access_token esteja formatado corretamente
    var $final_token_header {
      value = $tokens1.token
    }
  
    conditional {
      if (($tokens1.token|istarts_with:"access_token:") == false) {
        var.update $final_token_header {
          value = "access_token: " ~ $tokens1.token
        }
      }
    }
  
    // 6. Atualiza status para "Pagamento Iniciado"
    db.get STATUS_TRANSACAO {
      field_name = "status"
      field_value = "Pagamento Iniciado"
    } as $status_iniciado
  
    db.edit "TRANSAÇÃO" {
      field_name = "id"
      field_value = `$input.transacao_id`
      enforce_hidden_fields = false
      data = {statustransacao_id: `$status_iniciado.id`}
    } as $transacao_atualizada
  
    // 7. Chama a API de pagamento com token do cartão
    //    URL montada dinamicamente: /payments/{idpayment}/payWithCreditCard
    api.request {
      url = "https://api-sandbox.asaas.com/v3/payments/" ~ $transacao1.idpayment ~ "/payWithCreditCard"
      method = "POST"
      params = {creditCardToken: `$CARTAOTOKNZD1.token`}
      headers = [
        $final_token_header
        "Content-Type: application/json"
        "Accept: application/json"
        "User-Agent: XanoScript"
      ]
    } as $api_pagamento
  
    precondition ($api_pagamento.response.status == 200 || $api_pagamento.response.status == 201) {
      error = "Erro ao pagar cobrança: " ~ ($api_pagamento.response.result.errors.0.description|to_text)
    }
  
    // 8. Atualiza status para "Sucesso no Pagamento da Cobrança"
    db.get STATUS_TRANSACAO {
      field_name = "status"
      field_value = "Sucesso no Pagamento da Cobrança"
    } as $status_sucesso
  
    db.edit "TRANSAÇÃO" {
      field_name = "id"
      field_value = `$input.transacao_id`
      enforce_hidden_fields = false
      data = {statustransacao_id: `$status_sucesso.id`}
    } as $transacao_final
  
    var $status {
      value = {
        status    : true
        mensagem  : "Pagamento realizado com sucesso."
        idpayment : `$transacao1.idpayment`
        status_pag: `$api_pagamento.response.result.status`
        valor     : `$transacao1.valor`
      }
    }
  }

  response = $status
  guid = "vIipu5n0lxZ_MSOl_A9L_nfT2so"
}