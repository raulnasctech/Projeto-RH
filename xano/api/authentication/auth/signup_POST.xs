// Signup and retrieve an authentication token
query "auth/signup" verb=POST {
  api_group = "Authentication"

  input {
    text name?
    email email? filters=trim|lower
    text password?
    text cpf? filters=trim
    text celular? filters=trim
  }

  stack {
    // Check if a user record with that email exists
    db.get user {
      field_name = "email"
      field_value = $input.email
    } as $user
  
    // Verify that the email being used to sign up is unique
    precondition ($user == null) {
      error_type = "accessdenied"
      error = "This account is already in use."
    }
  
    // Create a new user record
    db.add user {
      enforce_hidden_fields = false
      data = {
        created_at: "now"
        name      : $input.name
        email     : $input.email
        cpf       : $input.cpf
        password  : $input.password
      }
    } as $user
  
    // Create an authentiction token
    security.create_auth_token {
      table = "user"
      extras = {}
      expiration = 86400
      id = $user.id
    } as $authToken
  
    // Create an event log for signup
    function.run "Getting Started Template/create_event_log" {
      input = {
        user_id   : $user.id
        account_id: 0
        action    : "signup"
        metadata  : $user
      }
    } as $event_log
  
    db.add CLIENTE {
      enforce_hidden_fields = false
      data = {
        user_id: $user.id
        celular: $input.celular
        cpf    : $input.cpf
      }
    } as $CLIENTE1
  }

  response = {authToken: $authToken, user_id: $user.id}
  tags = ["xano:quick-start"]
  guid = "rUG4j5xdPgFjFGPIKXqnl6q3lKo"
}