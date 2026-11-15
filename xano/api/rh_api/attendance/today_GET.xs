// Read today's attendance dashboard for Gestor RH
query "attendance/today" verb=GET {
  api_group = "rh_api"
  auth = "user"

  input {
  }

  stack {
    function.run "RH API/authorize employee manager" {
      input = {authenticated_user_id: $auth.id}
    } as $authorization

    function.run "RH API/get attendance clock" {
    } as $clock

    db.query employees {
      join = {
        employee_user: {
          table: "user"
          type: "left"
          where: $db.employees.user_id == $db.employee_user.id
        }
        employee_schedule: {
          table: "work_schedules"
          type: "left"
          where: $db.employees.id == $db.employee_schedule.employees_id
        }
      }

      where = ($db.employees.status|lower) == "ativo"

      eval = {
        employee_name: $db.employee_user.name
        weekly_schedule: $db.employee_schedule.weekly_schedule
      }

      output = [
        "id"
        "employee_name"
        "job_title"
        "status"
        "weekly_schedule"
      ]
      return = {type: "list"}
    } as $employees

    db.query attendance_punches {
      join = {
        employee: {
          table: "employees"
          type: "inner"
          where: $db.attendance_punches.employees_id == $db.employee.id
        }
      }

      where = $db.attendance_punches.work_date == $clock.work_date && ($db.employee.status|lower) == "ativo"
      sort = {punched_at: "asc"}
      output = [
        "id"
        "employees_id"
        "punch_type"
        "punched_at"
        "schedule_snapshot"
      ]
      return = {type: "list"}
    } as $punches
  }

  response = {
    work_date: $clock.work_date
    server_now: $clock.server_now
    employees: $employees
    punches: $punches
  }
  guid = "ATi2_iTQMpEc4jgSdrlniiZt9XU"
}
