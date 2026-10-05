// Query all ITEM records for the authenticated user
// Inclui detalhes do produto (nome e imagem) para completar o carrinho na visualização
query itemList verb=GET {
  api_group = "Event Logs"
  auth = "user"

  input {
  }

  stack {
    db.query ITEM {
      join = {
        produto: {
          table: "PRODUTO"
          where: $db.ITEM.produto_id == $db.produto.id
        }
      }
    
      where = $db.ITEM.cliente_id == $auth.id
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
    
      return = {type: "list"}
    } as $model
  }

  response = $model
  guid = "gDkTuI2pUKdbrU-73yW8an_EqBc"
}