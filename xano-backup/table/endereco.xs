// ENDERECO
table ENDERECO {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // logradouro
    text logradouro? filters=trim
  
    // numero
    text numero? filters=trim
  
    // complemento
    text complemento? filters=trim
  
    // bairro
    text bairro? filters=trim
  
    // referencia
    text referencia? filters=trim
  
    // padrao
    bool padrao?
  
    // cep
    int cep_id? {
      table = "CEP"
    }
  
    // referencia 
    int cliente_id? {
      table = "CLIENTE"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["sabor local "]
  guid = "93vkJJv_t6b9DzRDmPvnq-uE98E"
}