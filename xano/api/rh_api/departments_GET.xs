// Query all departments records
query departments verb=GET {
  api_group = "rh_api"
  auth = "user"

  input {
  }

  stack {
    function.run "RH API/authorize employee manager" {
      input = {authenticated_user_id: $auth.id}
    } as $authorization

    db.query departaments {
      eval = {
        id: $db.departaments.id,
        name: $db.departaments.nome
      }
      output = ["id", "name"]
      return = {type: "list"}
    } as $departments
  }

  response = $departments
}