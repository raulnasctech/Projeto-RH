query verificar_otp verb=POST {
  api_group = "Sendgrid Validation"

  input {
    text email? filters=trim
    text codigo_otp? filters=trim
  }

  stack {
    db.get user {
      field_name = "email"
      field_value = $input.email
    } as $user1
  
    precondition ($user1 != null) {
      error = "Usuário não encontrado."
    }
  
    precondition (($user1.codigo_otp|to_text) == ($input.codigo_otp|to_text)) {
      error = "O código inserido é inválido."
    }
  
    precondition ($user1.otp_expires_at > now) {
      error = "O código de verificação expirou."
    }
  
    db.edit user {
      field_name = "id"
      field_value = $user1.id
      enforce_hidden_fields = false
      data = {codigo_otp: "", otp_expires_at: null}
    } as $user2
  
    security.create_auth_token {
      table = "user"
      extras = {}
      expiration = 86400
      id = $user1
    } as $authToken
  }

  response = {
    user1                       : $authToken
    "E-mailverificadocomsucesso": '"E-mail verificado com sucesso!"'
  }

  guid = "5gehk-H6kIwF2-0vgX4xreyX-18"
}