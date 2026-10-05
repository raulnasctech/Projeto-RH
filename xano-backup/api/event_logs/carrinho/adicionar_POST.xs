// Endpoint para adicionar um item ao carrinho
// Retorna o pedido atualizado com seus itens detalhados (nome, imagem e preço)
query "carrinho/adicionar" verb=POST {
  api_group = "Event Logs"
  auth = "user"

  input {
    // ID do produto a ser adicionado
    int produto_id
  
    // Quantidade (opcional, padrão 1)
    int qtd?
  
    int pedido_aberto_id?
  }

  stack {
    // 1. Busca o cliente vinculado ao usuário logado
    db.get CLIENTE {
      field_name = "user_id"
      field_value = $auth.id
    } as $cliente_logado
  
    precondition ($cliente_logado != null) {
      error_type = "notfound"
      error = "Cliente não encontrado."
    }
  
    // 2. Busca o ID do status 'Criado' para pedidos em aberto
    db.query STATUS_PEDIDO {
      where = $db.STATUS_PEDIDO.status == "Criado"
      return = {type: "single"}
    } as $status_criado
  
    precondition ($status_criado != null) {
      error_type = "notfound"
      error = "Status 'Criado' não encontrado."
    }
  
    // 3. Busca os detalhes do produto para pegar o preço atual
    db.get PRODUTO {
      field_name = "id"
      field_value = $input.produto_id
    } as $produto
  
    precondition ($produto != null) {
      error_type = "notfound"
      error = "Produto não encontrado."
    }
  
    // 4. Busca se já existe um pedido aberto para este cliente
    db.query PEDIDO {
      where = $db.PEDIDO.cliente_id == $cliente_logado.id && $db.PEDIDO.status_pedido_id == $status_criado.id
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
            cliente_id      : $cliente_logado.id
            status_pedido_id: $status_criado.id
          }
        } as $pedido
      }
    }
  
    // 6. Define a quantidade e calcula o subtotal
    var $quantidade {
      value = $input.qtd ?? 1
    }
  
    var $subtotal {
      value = ($quantidade * $produto.preco)
    }
  
    // 7. Adiciona o item ao pedido
    db.add ITEM {
      enforce_hidden_fields = false
      data = {
        created_at    : now
        cliente_id    : $cliente_logado.id
        qtd           : $quantidade
        valor_unit    : $produto.preco
        subtotal      : $subtotal
        produto_id    : $produto.id
        status_item_id: 1
        item_pedido_id: $pedido.id
      }
    } as $novo_item
  
    db.get PRODUTO {
      field_name = "id"
      field_value = $input.produto_id
    } as $PRODUTO1
  
    // 8. Recalcula o valor total do pedido
    function.run recalculate_order_total {
      input = {pedido_id: $pedido.id}
    } as $total_recalculado
  
    // 9. Retorna o pedido completo com os itens detalhados (padronizado com a API pedido/aberto)
    db.query PEDIDO {
      where = $db.PEDIDO.id == $pedido.id
      return = {type: "single"}
      addon = [
        {
          name : "get_itens_pedido"
          input: {pedido_id: $output.id}
          as   : "itens"
        }
      ]
    } as $pedido_completo
  }

  response = $pedido_completo
  guid = "q2PqAVFlxpk-KIiGmAeB8NKzAgg"
}