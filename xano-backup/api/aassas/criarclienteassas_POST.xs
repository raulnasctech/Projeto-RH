// ════════════════════════════════════════════════════════════════════════════
// ENDPOINT 1 — criarclienteassas
// ════════════════════════════════════════════════════════════════════════════
// 5. Retorna o objeto do cliente (novo ou existente) em formato JSON
// Retorna o objeto do cliente com o ID do Asaas injetado
query criarclienteassas verb=POST {
  api_group = "AASSAS"

  input {
    text authtoken filters=trim
  }

  stack {
    // 1. Busca o usuário logado pelo authtoken via API interna
    api.request {
      url = "https://x8ki-letl-twmt.n7.xano.io/api:ddB1rUAm/auth/me"
      method = "GET"
      headers = ["Authorization: Bearer " ~ $input.authtoken]
    } as $auth_result
  
    // 2. Garante que o auth funcionou
    precondition ($auth_result.response.status == 200) {
      error = "Token inválido ou expirado. Faça login novamente."
    }
  
    // 3. Busca o registro completo do usuário diretamente no banco de dados
    // Isso garante que tenhamos todos os campos, como o CPF, que podem estar ausentes no auth_result
    db.get user {
      field_name = "id"
      field_value = $auth_result.response.result.id
    } as $usuario
  
    // 4. Busca o CLIENTE vinculado ao usuário no banco de dados (opcional, para retorno)
    db.get CLIENTE {
      field_name = "user_id"
      field_value = $usuario.id
    } as $cliente
  
    var $resultado {
      value = $cliente
    }
  
    var $asaas_id {
      value = ""
    }
  
    // 4. Estrutura Condicional (If/Else) ajustada conforme solicitado
    conditional {
      if ($usuario.customer_id_asaas == null || $usuario.customer_id_asaas == "") {
        // SE o customer_id_asaas é NULL: Cria no Asaas e salva os dados
      
        // 4.1. Busca o token do Asaas na tabela tokens
        db.get tokens {
          field_name = "plataforma"
          field_value = "Assas"
        } as $tokens_asaas
      
        precondition ($tokens_asaas != null) {
          error = "Token do Asaas não configurado na tabela tokens."
        }
      
        // Formatação do header access_token
        var $final_token_header {
          value = $tokens_asaas.token
        }
      
        conditional {
          if (($tokens_asaas.token|istarts_with:"access_token:") == false) {
            var.update $final_token_header {
              value = "access_token: " ~ $tokens_asaas.token
            }
          }
        }
      
        // 4.2. Limpa o CPF/CNPJ para conter apenas números
        // Utilizamos o CPF vindo diretamente do banco de dados ($usuario.cpf)
        var $cpf_limpo {
          value = "/[^0-9]/"
            |regex_replace:"":$usuario.cpf ?? ""
        }
      
        precondition (($cpf_limpo|strlen) >= 11) {
          error = "O CPF do usuário é inválido ou não informado no banco de dados."
        }
      
        // 4.3. Chamada de API para o Asaas para criar o cliente
        api.request {
          url = "https://api-sandbox.asaas.com/v3/customers"
          method = "POST"
          params = {name: $usuario.name, cpfCnpj: $cpf_limpo}
          headers = [
            $final_token_header
            "Content-Type: application/json"
            "Accept: application/json"
            "User-Agent: IntegracaoXano"
          ]
        } as $api_asaas
      
        precondition ($api_asaas.response.status == 200 || $api_asaas.response.status == 201) {
          error = "Erro ao criar cliente no Asaas: " ~ ($api_asaas.response.result.errors.0.description|to_text)
        }
      
        // 4.4. Salva o ID do cliente Asaas na tabela 'user' (vínculo ao auth.id)
        db.edit user {
          field_name = "id"
          field_value = $usuario.id
          enforce_hidden_fields = false
          data = {customer_id_asaas: $api_asaas.response.result.id}
        } as $updated_user
      
        // 4.5. Cria o registro na tabela CLIENTE se não existir
        conditional {
          if ($cliente == null) {
            db.add CLIENTE {
              enforce_hidden_fields = false
              data = {
                user_id: $usuario.id
                cpf    : $usuario.cpf
                celular: $usuario.celular
              }
            } as $novo_cliente
          
            var.update $resultado {
              value = $novo_cliente
            }
          }
        }
      
        var.update $asaas_id {
          value = $api_asaas.response.result.id
        }
      }
    
      else {
        // SENÃO (ELSE): Apenas retorna o valor que já está gravado em 'usuario.customer_id_asaas'
        var.update $asaas_id {
          value = $usuario.customer_id_asaas
        }
      }
    }
  }

  response = $resultado
    |set:"customer_id_asaas":$asaas_id
  guid = "MI9wLMpzpCUu0x5WJuuNBk7kKgk"
}