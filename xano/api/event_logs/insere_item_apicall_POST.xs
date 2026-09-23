// Endpoint para inserir um item em um pedido via API Call
// Se o produto já existir no pedido informado, a quantidade será incrementada
// Garante que o preço seja buscado da tabela PRODUTO para consistência
query insere_item_apicall verb=POST {
  api_group = "Event Logs"
  auth = "user"

  input {
    // ID do pedido em aberto
    int pedido_aberto_id?
  
    // Quantidade a adicionar
    int qtd?
  
    // ID do produto
    int produto_id?
  }

  stack {
    // 1. Buscar informações do produto para garantir o preço atual
    db.get PRODUTO {
      field_name = "id"
      field_value = $input.produto_id
    } as $produto
  
    precondition ($produto != null) {
      error_type = "notfound"
      error = "Produto não encontrado."
    }
  
    // 2. Buscar informações do cliente
    db.get CLIENTE {
      field_name = "user_id"
      field_value = $auth.id
    } as $cliente
  
    var $quantidade_adicionar {
      value = $input.qtd ?? 1
    }
  
    // 3. Verificar se este produto já existe no pedido informado
    db.query ITEM {
      where = $db.ITEM.item_pedido_id == $input.pedido_aberto_id && $db.ITEM.produto_id == $input.produto_id
      return = {type: "single"}
    } as $item_existente
  
    // 4. Lógica de Adicionar ou Atualizar
    conditional {
      if ($item_existente != null) {
        // Atualiza item existente
        var $nova_qtd {
          value = $item_existente.qtd + $quantidade_adicionar
        }
      
        var $novo_subtotal {
          value = $nova_qtd * $produto.preco
        }
      
        db.edit ITEM {
          field_name = "id"
          field_value = $item_existente.id
          enforce_hidden_fields = false
          data = {
            qtd       : $nova_qtd
            subtotal  : $novo_subtotal
            valor_unit: $produto.preco
          }
        } as $item_final
      }
    
      else {
        // Cria novo item
        var $subtotal {
          value = $quantidade_adicionar * $produto.preco
        }
      
        db.add ITEM {
          enforce_hidden_fields = false
          data = {
            created_at    : now
            cliente_id    : $cliente.id
            qtd           : $quantidade_adicionar
            valor_unit    : $produto.preco
            subtotal      : $subtotal
            produto_id    : $produto.id
            status_item_id: 1
            item_pedido_id: $input.pedido_aberto_id
          }
        } as $item_final
      }
    }
  
    // 5. Recalcular o total do pedido se houver um ID de pedido
    conditional {
      if ($input.pedido_aberto_id != null) {
        function.run recalculate_order_total {
          input = {pedido_id: $input.pedido_aberto_id}
        } as $total_recalculado
      }
    }
  
    // 6. Retorna o item atualizado com detalhes
    db.query ITEM {
      join = {
        produto: {
          table: "PRODUTO"
          where: $db.ITEM.produto_id == $db.produto.id
        }
      }
    
      where = $db.ITEM.id == $item_final.id
      eval = {
        id            : $db.ITEM.id
        created_at    : $db.ITEM.created_at
        cliente_id    : $db.ITEM.cliente_id
        qtd           : $db.ITEM.qtd
        valor_unit    : $db.ITEM.valor_unit
        subtotal      : $db.ITEM.subtotal
        produto_id    : $db.ITEM.produto_id
        status_item_id: $db.ITEM.status_item_id
        item_pedido_id: $db.ITEM.item_pedido_id
        nome          : $db.produto.nome
        url_imagem    : $db.produto.url_imagem
      }
    
      return = {type: "single"}
      output = [
        "id"
        "created_at"
        "cliente_id"
        "qtd"
        "valor_unit"
        "subtotal"
        "produto_id"
        "status_item_id"
        "item_pedido_id"
        "nome"
        "url_imagem"
      ]
    } as $item_completo
  }

  response = $item_completo
  guid = "lEeu_Bv6r6xlAFcoKUdh0nV6yB8"
}