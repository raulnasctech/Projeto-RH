// Remove um item do carrinho e atualiza o total do pedido
query "remover_item/{item_id}" verb=DELETE {
  api_group = "pedido"
  auth = "user"

  input {
    // ID do item a ser removido (tabela ITEM)
    int item_id
  }

  stack {
    // 1. Busca o cliente vinculado ao usuário logado para segurança
    db.get CLIENTE {
      field_name = "user_id"
      field_value = $auth.id
    } as $cliente
  
    precondition ($cliente != null) {
      error_type = "notfound"
      error = "Cliente não encontrado."
    }
  
    // 2. Busca o item para verificar a propriedade e obter o ID do pedido
    db.get ITEM {
      field_name = "id"
      field_value = $input.item_id
    } as $item
  
    precondition ($item != null) {
      error_type = "notfound"
      error = "Item não encontrado."
    }
  
    // 3. Verifica se o item pertence ao cliente logado
    precondition ($item.cliente_id == $cliente.id) {
      error_type = "accessdenied"
      error = "Você não tem permissão para remover este item."
    }
  
    var $pedido_id {
      value = $item.item_pedido_id
    }
  
    // 4. Deleta o item da tabela ITEM
    db.del ITEM {
      field_name = "id"
      field_value = $input.item_id
    }
  
    // 5. Recalcula o total do pedido através da função
    function.run recalculate_order_total {
      input = {pedido_id: $pedido_id}
    } as $total_recalculado
  
    // 6. Retorna o estado atualizado do pedido
    db.query PEDIDO {
      where = $db.PEDIDO.id == $pedido_id
      return = {type: "single"}
      addon = [
        {
          name : "get_itens_pedido"
          input: {pedido_id: $output.id}
          as   : "itens"
        }
      ]
    } as $carrinho_atualizado
  }

  response = $carrinho_atualizado
  guid = "nwsI8nbUoiVoCZfz-rAn58iJZbI"
}