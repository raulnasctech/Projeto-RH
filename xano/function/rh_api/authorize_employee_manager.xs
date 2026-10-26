function "RH API/authorize employee manager" {
  input {
    int authenticated_user_id
  }

  stack {
    db.get user {
      field_name = "id"
      field_value = $input.authenticated_user_id
      output = ["role"]
    } as $authenticated_user
  
    precondition ($authenticated_user != null) {
      error_type = "accessdenied"
      error = "Acesso negado."
    }
  
    precondition ($authenticated_user.role == "Gestor RH" || $authenticated_user.role == "" || $authenticated_user.role == null) {
      error_type = "accessdenied"
      error = "Acesso negado."
    }
  }

  response = null
  guid = "q8s4R5xC_GHNijcE4aciHltZnBA"
}
