// Stores user information and allows the user to authenticate  against
table user {
  auth = true

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text name filters=trim
    email? email filters=trim|lower
    text cpf? filters=trim
    text celular? filters=trim
    password? password filters=min:8|minAlpha:1|minDigit:1
    text role? filters=trim
  
    // referencia
    int papel_id? {
      table = "PAPEL"
    }
  
    int account_id? {
      table = "account"
    }
  
    text codigo_otp? filters=trim
    timestamp? otp_expires_at?
    text customer_id_asaas? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "email", op: "asc"}]}
  ]

  tags = ["xano:quick-start", "sabor local "]
  guid = "g8tpjso2orFaPgdxKGzuuR66M1k"
}