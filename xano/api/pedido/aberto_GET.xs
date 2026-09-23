// Endpoint para buscar o carrinho (pedido aberto) do usuário logado
// Inclui automaticamente a lista de itens com nome, imagem e preço do produto
query aberto verb=GET {
  api_group = "pedido"
  auth = "user"

  input {
  }

  stack {
    // 1. Busca o registro de CLIENTE vinculado ao usuário logado
    db.get CLIENTE {
      field_name = "user_id"
      field_value = $auth.id
    } as $cliente
  
    precondition ($cliente != null) {
      error_type = "notfound"
      error = "Cliente não encontrado."
    }
  
    // 2. Busca o ID do status "Criado" (representa o carrinho)
    db.query STATUS_PEDIDO {
      where = $db.STATUS_PEDIDO.status == "Criado"
      return = {type: "single"}
    } as $status_aberto
  
    precondition ($status_aberto != null) {
      error_type = "notfound"
      error = "Status de carrinho 'Criado' não encontrado."
    }
  
    // 3. Busca o pedido aberto com o addon de itens detalhados
    db.query PEDIDO {
      where = $db.PEDIDO.cliente_id == $cliente.id && $db.PEDIDO.status_pedido_id == $status_aberto.id
      return = {type: "single"}
      addon = [
        {
          name : "get_itens_pedido"
          input: {pedido_id: $output.id}
          as   : "itens"
        }
      ]
    } as $pedido_aberto
  }

  response = $pedido_aberto
  guid = "npY95ckNe6XnNu76C82TE4FFOAU"
}