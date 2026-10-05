// ════════════════════════════════════════════════════════════════════════════
// ENDPOINT 3 — criarcob
// Cria uma cobrança no Asaas e salva na tabela TRANSAÇÃO
// Inputs: authtoken, pedido_id, valor, datavenc (YYYY-MM-DD), descricao
// ════════════════════════════════════════════════════════════════════════════
query criarcob verb=POST {
  api_group = "AASSAS"

  input {
    text authtoken filters=trim
    int pedido_id
    decimal valor
    text datavenc filters=trim
    text descricao filters=trim
  }

  stack {
    // 1. Busca o usuário logado para validar o token
    api.request {
      url = "https://x8ki-letl-twmt.n7.xano.io/api:ddB1rUAm/auth/me"
      method = "GET"
      headers = ["Authorization: Bearer " ~ $input.authtoken]
    } as $auth_result
  
    precondition ($auth_result.response.status == 200) {
      error = "Token inválido ou expirado. Faça login novamente."
    }
  
    var $usuario {
      value = $auth_result.response.result
    }
  
    // 2. Captura e valida inputs básicos
    var $valor_cob {
      value = $input.valor|to_decimal
    }
  
    var $vencimento {
      value = $input.datavenc
    }
  
    var $desc {
      value = $input.descricao
    }
  
    var $ped_id {
      value = $input.pedido_id
    }
  
    precondition (($vencimento|strlen) > 0) {
      error = "O parâmetro datavenc (data de vencimento) deve ser informado no formato YYYY-MM-DD."
    }
  
    // 3. Busca o CLIENTE associado ao usuário
    db.get CLIENTE {
      field_name = "user_id"
      field_value = $usuario.id
    } as $cliente
  
    precondition ($cliente != null) {
      error = "Cliente não encontrado para este usuário."
    }
  
    // 4. Busca CARTAOTOKNZD (precisa do codigoclienteassas do cliente)
    db.get CARTAOTOKNZD {
      field_name = "cliente_id"
      field_value = $cliente.id
    } as $CARTAOTOKNZD1
  
    precondition ($CARTAOTOKNZD1 != null && ($CARTAOTOKNZD1.codigoclienteassas != "")) {
      error = "Cliente não criado no Asaas. Rode criarclienteassas primeiro."
    }
  
    precondition (($CARTAOTOKNZD1.token|strlen) > 0) {
      error = "Cartão não tokenizado. É necessário realizar a tokenização do cartão antes de criar uma cobrança de cartão de crédito."
    }
  
    // 5. Busca o token de API do Asaas na tabela de tokens
    db.get tokens {
      field_name = "plataforma"
      field_value = "Assas"
    } as $tokens1
  
    precondition ($tokens1 != null) {
      error = "Token do Asaas não configurado na tabela tokens."
    }
  
    // Formata o header access_token corretamente
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
  
    // 6. Prepara o payload da cobrança como um objeto literal robusto
    var $payload {
      value = {
        customer       : $CARTAOTOKNZD1.codigoclienteassas
        billingType    : "CREDIT_CARD"
        value          : $valor_cob
        dueDate        : $vencimento
        description    : $desc
        creditCardToken: $CARTAOTOKNZD1.token
      }
    }
  
    // Log do payload para depuração (visível no debugger do Xano)
    debug.log {
      value = $payload
    }
  
    // 7. Cria a cobrança no Asaas
    api.request {
      url = "https://api-sandbox.asaas.com/v3/payments"
      method = "POST"
      params = $payload
      headers = [
        $final_token_header
        "Content-Type: application/json"
        "Accept: application/json"
        "User-Agent: XanoScript"
      ]
    } as $api_cobranca
  
    precondition ($api_cobranca.response.status == 200 || $api_cobranca.response.status == 201) {
      error = "Erro ao criar cobrança: " ~ ($api_cobranca.response.result.errors.0.description|to_text)
    }
  
    // 8. Busca status "Cobrança Criada" para registro interno
    db.get STATUS_TRANSACAO {
      field_name = "status"
      field_value = "Cobrança Criada"
    } as $status_criada
  
    // 9. Salva o registro da transação no banco de dados local
    db.add "TRANSAÇÃO" {
      enforce_hidden_fields = false
      data = {
        clienteassas       : $CARTAOTOKNZD1.codigoclienteassas
        idpayment          : $api_cobranca.response.result.id
        tipo               : "CREDIT_CARD"
        valor              : $valor_cob
        datavenc           : $vencimento
        descricao          : $desc
        statustransacao_id : $status_criada.id
        pedido_id          : $ped_id
        status_transacao_id: 0
      }
    } as $transacao1
  
    // 10. Prepara a resposta de sucesso
    var $status {
      value = {
        status      : true
        mensagem    : "Cobrança criada com sucesso."
        idpayment   : $api_cobranca.response.result.id
        transacao_id: $transacao1.id
      }
    }
  }

  response = $status
  guid = "tq1sBLYf87KmcjTcz-Y6bUKJX_U"
}