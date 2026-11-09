// Query all vacation_requests records
query vacation_requests verb=GET {
  api_group = "rh_api"
  auth = "user"

  input {
  }

  stack {
    function.run "RH API/authorize employee manager" {
      input = {authenticated_user_id: $auth.id}
    } as $authorization

    db.query vacation_requests {
      join = {
        employee: {
          table: "employees"
          type: "left"
          where: $db.vacation_requests.employees_id == $db.employee.id
        }
        employee_user: {
          table: "user"
          type: "left"
          where: $db.employee.user_id == $db.employee_user.id
        }
      }

      eval = {
        employee_name: $db.employee_user.name
      }

      output = [
        "id"
        "employees_id"
        "start_date"
        "end_date"
        "status"
        "employee_name"
      ]
      return = {type: "list"}
    } as $vacation_requests
  }

  response = $vacation_requests
  guid = "0MbYWxE5wGusg1gHiLdva--U2m4"
}