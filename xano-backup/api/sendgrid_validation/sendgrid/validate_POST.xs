// This endpoint is used to validate that sendgrid is working.
query "sendgrid/validate" verb=POST {
  api_group = "Sendgrid Validation"

  input {
    email email
  }

  stack {
    // Busca o usuário pelo e-mail fornecido
    db.get user {
      field_name = "email"
      field_value = $input.email
    } as $user1
  
    // Verifica se o usuário existe para evitar erro de variável não encontrada
    precondition ($user1 != null) {
      error_type = "notfound"
      error = "Usuário não encontrado com o e-mail informado."
    }
  
    // Gera um código OTP aleatório de 6 dígitos
    security.random_number {
      min = 100000
      max = 999999
    } as $codigo_otp
  
    // Define a expiração para 5 minutos (300 segundos) a partir de agora
    var $expiracao {
      value = now|add_secs_to_timestamp:300
    }
  
    // Atualiza o registro do usuário com o código OTP e data de expiração
    db.edit user {
      field_name = "id"
      field_value = $user1.id
      enforce_hidden_fields = false
      data = {codigo_otp: $codigo_otp, otp_expires_at: $expiracao}
    } as $user2
  
    // Envia o e-mail com o código OTP via SendGrid
    function.run sendgrid_basic_send {
      input = {
        to_email: $input.email
        subject : "validaçao sabor local"
        body    : $codigo_otp
      }
    } as $func_1
  }

  response = {status: "success"}
  guid = "tSSPmFXre3-MQ55biKk27v4NBxg"
}