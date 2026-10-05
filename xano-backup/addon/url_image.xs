addon url_image {
  input {
    int PRODUTO_id? {
      table = "PRODUTO"
    }
  }

  stack {
    db.query PRODUTO {
      where = $db.PRODUTO.id == $input.PRODUTO_id
      return = {type: "count"}
    }
  }

  guid = "sMP7WfZolDa6NlzAtdyVDAx6Rhc"
}