// Options for the employee creation form
query "employee-form-options" verb=GET {
  api_group = "rh_api"
  auth = "user"

  input {
  }

  stack {
    function.run "RH API/authorize employee manager" {
      input = {authenticated_user_id: $auth.id}
    } as $authorization

    db.query departaments {
      output = ["id", "nome"]
      return = {type: "list"}
    } as $departments

    db.query user {
      join = {
        linked_employee: {
          table: "employees"
          type: "left"
          where: $db.user.id == $db.linked_employee.user_id
        }
      }
      where = $db.linked_employee.id == null && $db.user.id != $auth.id
      output = ["id", "name"]
      return = {type: "list"}
    } as $users
  }

  response = {departments: $departments, users: $users}
}
