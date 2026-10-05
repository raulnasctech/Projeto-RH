// Adiciona um item ao carrinho (pedido com status 'Criado')
// Se o pedido não existir, um novo será criado para o cliente logado
query adicionar verb=POST {
  api_group = "pedido"
  auth = "user"

  input {
    // ID do produto a ser adicionado
    int produto_id
  
    // Quantidade (opcional, padrão 1)
    int qtd?
  }

  stack {
    // 1. Busca o cliente vinculado ao usuário logado
    db.get CLIENTE {
      field_name = "user_id"
      field_value = $auth.id
    } as $cliente
  
    precondition ($cliente != null) {
      error_type = "notfound"
      error = "Cliente não encontrado."
    }
  
    // 2. Busca os detalhes do produto para pegar o preço
    db.get PRODUTO {
      field_name = "id"
      field_value = $input.produto_id
    } as $produto
  
    precondition ($produto != null) {
      error_type = "notfound"
      error = "Produto não encontrado."
    }
  
    // 3. Busca o ID do status 'Criado'
    db.query STATUS_PEDIDO {
      where = $db.STATUS_PEDIDO.status == "Criado"
      return = {type: "single"}
    } as $status_carrinho
  
    precondition ($status_carrinho != null) {
      error_type = "notfound"
      error = "Status de pedido 'Criado' não configurado."
    }
  
    // 4. Busca se já existe um pedido aberto para este cliente
    db.query PEDIDO {
      where = $db.PEDIDO.cliente_id == $cliente.id && $db.PEDIDO.status_pedido_id == $status_carrinho.id
      return = {type: "single"}
    } as $pedido
  
    // 5. Cria o pedido se não existir
    conditional {
      if ($pedido == null) {
        db.add PEDIDO {
          enforce_hidden_fields = false
          data = {
            created_at      : now
            total           : 0
            cliente_id      : $cliente.id
            status_pedido_id: $status_carrinho.id
          }
        } as $pedido
      }
    }
  
    // 6. Calcula subtotal do novo item
    var $quantidade {
      value = $input.qtd ?? 1
    }
  
    var $subtotal {
      value = $quantidade * $produto.preco
    }
  
    // 7. Adiciona o item ao pedido
    db.add ITEM {
      enforce_hidden_fields = false
      data = {
        created_at    : now
        cliente_id    : $cliente.id
        qtd           : $quantidade
        valor_unit    : $produto.preco
        subtotal      : $subtotal
        produto_id    : $produto.id
        status_item_id: 1
        item_pedido_id: $pedido.id
      }
    } as $novo_item
  
    // 8. Recalcula o total do pedido via função existente
    function.run recalculate_order_total {
      input = {pedido_id: $pedido.id}
    } as $total_recalculado
  
    // 9. Retorna o pedido completo com os itens (usando o addon atualizado)
    db.query PEDIDO {
      where = $db.PEDIDO.id == $pedido.id
      return = {type: "single"}
      addon = [
        {
          name : "get_itens_pedido"
          input: {pedido_id: $output.id}
          as   : "itens"
        }
        {
          name : "PRODUTO"
          input: {PRODUTO_id: ""}
          as   : "_produto"
        }
      ]
    } as $carrinho_completo
  }

  response = $carrinho_completo
  guid = "UiaTZEg0jdM_DcAuJ-wLQePa-Z0"
}