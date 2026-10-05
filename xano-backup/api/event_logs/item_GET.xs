// Query all ITEM records
// Retorna os itens com os detalhes do produto (nome, imagem)
query item verb=GET {
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
    
      addon = [
        {
          name : "PRODUTO"
          input: {PRODUTO_id: $output.produto_id}
          as   : "_produto"
        }
      ]
    } as $item
  }

  response = $item
  guid = "F3LenHVqBIBxC8L1yhWPb0tvzJw"
}