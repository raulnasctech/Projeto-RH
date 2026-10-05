// Addon para buscar os itens de um pedido específico
// Recebe o ID do pedido e retorna a lista de itens associados
// Agora inclui o nome, imagem e preço original do produto através de um join
addon get_itens_pedido {
  input {
    // ID do pedido para o qual buscar itens
    int pedido_id
  }

  stack {
    db.query ITEM {
      join = {
        produto: {
          table: "PRODUTO"
          where: $db.ITEM.produto_id == $db.produto.id
        }
      }
    
      where = $db.ITEM.item_pedido_id == $input.pedido_id
      eval = {
        id                  : $db.ITEM.id
        created_at          : $db.ITEM.created_at
        cliente_id          : $db.ITEM.cliente_id
        qtd                 : $db.ITEM.qtd
        valor_unit          : $db.ITEM.valor_unit
        subtotal            : $db.ITEM.subtotal
        produto_id          : $db.ITEM.produto_id
        status_item_id      : $db.ITEM.status_item_id
        item_pedido_id      : $db.ITEM.item_pedido_id
        nome                : $db.produto.nome
        url_imagem          : $db.produto.url_imagem
        preco_unitario_atual: $db.produto.preco
      }
    
      return = {type: "list"}
    }
  }

  guid = "Xk3zf2Xgp6e7ycUbKgcdauReUo4"
}