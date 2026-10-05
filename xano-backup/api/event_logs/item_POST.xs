// Add ITEM record
// Retorna o item criado incluindo detalhes do produto (nome, imagem)
query item verb=POST {
  api_group = "Event Logs"

  input {
    // Aceita todos os campos da tabela ITEM como entrada
    dblink {
      table = "ITEM"
    }
  }

  stack {
    // Calcula o subtotal inicial baseado na entrada (qtd * valor_unit)
    var $subtotal_calculado {
      value = ($input.qtd * $input.valor_unit)
    }
  
    // Adiciona o registro na tabela ITEM
    db.add ITEM {
      enforce_hidden_fields = false
      data = {
        created_at    : now
        cliente_id    : $input.cliente_id
        qtd           : $input.qtd
        valor_unit    : $input.valor_unit
        subtotal      : $subtotal_calculado
        produto_id    : $input.produto_id
        status_item_id: $input.status_item_id
        item_pedido_id: $input.item_pedido_id
      }
    } as $item
  
    // Se o item estiver associado a um pedido, recalcula o total do pedido
    conditional {
      if ($item.item_pedido_id != null) {
        function.run recalculate_order_total {
          input = {pedido_id: $item.item_pedido_id}
        } as $novo_total
      }
    }
  
    // Busca o item recém-criado com os detalhes do produto para a resposta ser completa
    db.query ITEM {
      join = {
        produto: {
          table: "PRODUTO"
          where: $db.ITEM.produto_id == $db.produto.id
        }
      }
    
      where = $db.ITEM.id == $item.id
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
  guid = "7YWR7o5_Ws_es_UrIiWhqPYqhMg"
}