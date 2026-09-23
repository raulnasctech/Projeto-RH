// Get ITEM record
query "item/{item_id}" verb=GET {
  api_group = "Event Logs"

  input {
    int item_id? filters=min:1
  }

  stack {
    db.get ITEM {
      field_name = "id"
      field_value = $input.item_id
      addon = [
        {
          name  : "PRODUTO"
          output: [
            "nome"
            "descricao"
            "qtd_disp"
            "url_imagem"
            "preco"
            "precisa_produzir"
          ]
          input : {PRODUTO_id: $output.produto_id}
          as    : "_produto"
        }
      ]
    } as $item
  
    precondition ($item != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $item
  guid = "7YXxi9D4Hny6GGzz5Zuux2qmhiQ"
}