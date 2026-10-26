// Query all employees records
query employees verb=GET {
  api_group = "rh_api"
  auth = "user"

  input {
  }

  stack {
    function.run "RH API/authorize employee manager" {
      input = {authenticated_user_id: $auth.id}
    } as $authorization

    db.query employees {
      join = {
        employee_user: {
          table: "user"
          type: "left"
          where: $db.employees.user_id == $db.employee_user.id
        }
        employee_department: {
          table: "departaments"
          type: "left"
          where: $db.employees.departaments_id == $db.employee_department.id
        }
      }

      eval = {
        employee_name: $db.employees.name ?? $db.employee_user.name ?? "Não informado"
        department: $db.employee_department.nome ?? "Não informado"
      }

      output = ["id", "employee_name", "department", "job_title", "admissao", "status"]
      return = {type: "list"}
    } as $employees
  }

  response = $employees
  guid = "xWRaXUKGQM0DGRv15cDK2wgZH00"
}