// Read the authenticated employee's attendance for today
query "attendance/me" verb=GET {
  api_group = "rh_api"
  auth = "user"

  input {
  }

  stack {
    function.run "RH API/get attendance clock" {
    } as $clock

    db.query employees {
      where = $db.employees.user_id == $auth.id
      output = ["id", "user_id", "status"]
      return = {type: "list"}
    } as $linked_employees

    precondition (($linked_employees|count) == 1) {
      error_type = "accessdenied"
      error = "A conta deve estar vinculada a exatamente um colaborador."
    }

    var $employee {
      value = $linked_employees.0
    }

    precondition (($employee.status|lower) == "ativo") {
      error_type = "accessdenied"
      error = "Somente colaboradores ativos podem acessar o ponto."
    }

    db.get user {
      field_name = "id"
      field_value = $employee.user_id
      output = ["name"]
    } as $user

    db.get work_schedules {
      field_name = "employees_id"
      field_value = $employee.id
      output = ["weekly_schedule"]
    } as $work_schedule

    var $schedule_day {
      value = null
    }

    conditional {
      if ($work_schedule != null) {
        var.update $schedule_day {
          value = $work_schedule.weekly_schedule|get:$clock.weekday
        }
      }
    }

    db.query attendance_punches {
      where = $db.attendance_punches.employees_id == $employee.id && $db.attendance_punches.work_date == $clock.work_date
      sort = {punched_at: "asc"}
      output = ["id", "punch_type", "punched_at", "schedule_snapshot"]
      return = {type: "list"}
    } as $punches

    db.query attendance_punches {
      where = $db.attendance_punches.employees_id == $employee.id && $db.attendance_punches.work_date == $clock.work_date && $db.attendance_punches.punch_type == "entry"
      return = {type: "single"}
      output = ["schedule_snapshot"]
    } as $entry

    var $schedule_snapshot {
      value = $entry.schedule_snapshot ?? $schedule_day
    }
  }

  response = {
    employee: {
      id: $employee.id
      employee_name: $user.name ?? "Não informado"
      status: $employee.status
    }
    work_date: $clock.work_date
    server_now: $clock.server_now
    schedule: $schedule_snapshot
    punches: $punches
  }
  guid = "QQCMr0y9I0Eb2FC5D6jqvYlOGMI"
}
