// Recalcula o valor total de um pedido baseado nos subtotais de seus itens
// Calcula a soma dos subtotais dos itens de um pedido e atualiza o total na tabela PEDIDO
function recalculate_order_total {
  input {
    // ID do pedido a ser recalculado
    // O ID do registro na tabela PEDIDO
    int pedido_id
  }

  stack {
    // Busca todos os itens associados a este pedido
    db.query ITEM {
      where = $db.ITEM.item_pedido_id == $input.pedido_id
      return = {type: "list"}
    } as $itens
  
    // Calcula a soma de todos os subtotais
    // Se não houver itens, o total será 0
    var $total {
      value = ($itens|map:$$.subtotal|sum) ?? 0
    }
  
    // Atualiza a tabela PEDIDO com o novo total
    db.edit PEDIDO {
      field_name = "id"
      field_value = $input.pedido_id
      enforce_hidden_fields = false
      data = {total: $total}
    } as $updated_pedido
  }

  response = $total
  guid = "ztCLaVboFnP4Mn2a0S_9oKyIYpc"
}