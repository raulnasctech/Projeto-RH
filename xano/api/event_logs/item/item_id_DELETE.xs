// Remove um item do carrinho (tabela ITEM) e atualiza o total do pedido
query "item/{item_id}" verb=DELETE {
  api_group = "Event Logs"
  auth = "user"

  input {
    // ID do registro na tabela ITEM (não o produto_id)
    int item_id filters=min:1
  }

  stack {
    // 1. Buscar o item para obter o pedido_id e validar propriedade
    db.get ITEM {
      field_name = "id"
      field_value = $input.item_id
    } as $item
  
    precondition ($item != null) {
      error_type = "notfound"
      error = "Item não encontrado no carrinho."
    }
  
    // 2. Buscar o cliente para validar segurança
    db.get CLIENTE {
      field_name = "user_id"
      field_value = $auth.id
    } as $cliente
  
    precondition ($item.cliente_id == $cliente.id) {
      error_type = "accessdenied"
      error = "Você não tem permissão para remover este item."
    }
  
    var $pedido_id {
      value = $item.item_pedido_id
    }
  
    // 3. Deletar o item
    db.del ITEM {
      field_name = "id"
      field_value = $input.item_id
    }
  
    // 4. Recalcular o total do pedido
    conditional {
      if ($pedido_id != null) {
        function.run recalculate_order_total {
          input = {pedido_id: $pedido_id}
        } as $total_recalculado
      }
    }
  }

  response = {success: true, message: "Item removido com sucesso."}
  guid = "stjVC0ny7Vwkls-hDBENK-0bwAE"
}