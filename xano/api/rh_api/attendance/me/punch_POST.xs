// Record only the next attendance punch for the authenticated employee
query "attendance/me/punch" verb=POST {
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
      error = "Somente colaboradores ativos podem registrar ponto."
    }

    db.get work_schedules {
      field_name = "employees_id"
      field_value = $employee.id
      output = ["weekly_schedule"]
    } as $work_schedule

    precondition ($work_schedule != null) {
      error_type = "badrequest"
      error = "Não há jornada cadastrada para este colaborador."
    }

    var $schedule_day {
      value = $work_schedule.weekly_schedule|get:$clock.weekday
    }

    precondition ($schedule_day != null && $schedule_day.is_workday == true) {
      error_type = "badrequest"
      error = "Não há jornada de trabalho prevista para hoje."
    }

    db.query attendance_punches {
      where = $db.attendance_punches.employees_id == $employee.id && $db.attendance_punches.work_date == $clock.work_date
      sort = {punched_at: "asc"}
      output = ["id", "punch_type", "punched_at"]
      return = {type: "list"}
    } as $punches

    var $punch_count {
      value = $punches|count
    }

    precondition ($punch_count < 4) {
      error_type = "badrequest"
      error = "Todas as batidas previstas para hoje já foram registradas."
    }

    precondition (
      $punch_count == 0
      || (
        $punch_count == 1
        && $punches.0.punch_type == "entry"
      )
      || (
        $punch_count == 2
        && $schedule_day.break_start_minute != null
        && $punches.0.punch_type == "entry"
        && $punches.1.punch_type == "break_start"
      )
      || (
        $punch_count == 3
        && $schedule_day.break_start_minute != null
        && $punches.0.punch_type == "entry"
        && $punches.1.punch_type == "break_start"
        && $punches.2.punch_type == "break_end"
      )
    ) {
      error_type = "badrequest"
      error = "As batidas existentes estão incompletas ou fora de ordem."
    }

    conditional {
      if ($punch_count == 0) {
        precondition ($clock.current_minute >= $schedule_day.start_minute) {
          error_type = "badrequest"
          error = "A entrada ainda não está liberada."
        }

        db.add attendance_punches {
          data = {
            employees_id: $employee.id
            work_date: $clock.work_date
            punch_type: "entry"
            created_at: "now"
            punched_at: "now"
            schedule_snapshot: $schedule_day
          }
        } as $entry
      }
      elseif ($punch_count == 1 && $schedule_day.break_start_minute == null) {
        precondition ($clock.current_minute >= $schedule_day.end_minute) {
          error_type = "badrequest"
          error = "A saída final ainda não está liberada."
        }

        db.add attendance_punches {
          data = {
            employees_id: $employee.id
            work_date: $clock.work_date
            punch_type: "exit"
            punched_at: "now"
          }
        } as $exit_without_break
      }
      elseif ($punch_count == 1 && $schedule_day.break_start_minute != null) {
        precondition ($clock.current_minute >= $schedule_day.break_start_minute) {
          error_type = "badrequest"
          error = "A saída para intervalo ainda não está liberada."
        }

        db.add attendance_punches {
          data = {
            employees_id: $employee.id
            work_date: $clock.work_date
            punch_type: "break_start"
            punched_at: "now"
          }
        } as $break_start
      }
      elseif ($punch_count == 2 && $schedule_day.break_start_minute != null) {
        precondition ($clock.current_minute >= $schedule_day.break_end_minute) {
          error_type = "badrequest"
          error = "O retorno do intervalo ainda não está liberado."
        }

        db.add attendance_punches {
          data = {
            employees_id: $employee.id
            work_date: $clock.work_date
            punch_type: "break_end"
            punched_at: "now"
          }
        } as $break_end
      }
      elseif ($punch_count == 3 && $schedule_day.break_start_minute != null) {
        precondition ($clock.current_minute >= $schedule_day.end_minute) {
          error_type = "badrequest"
          error = "A saída final ainda não está liberada."
        }

        db.add attendance_punches {
          data = {
            employees_id: $employee.id
            work_date: $clock.work_date
            punch_type: "exit"
            punched_at: "now"
          }
        } as $exit_after_break
      }
      else {
        precondition (false) {
          error_type = "badrequest"
          error = "Não há outra batida prevista para esta jornada."
        }
      }
    }

    db.get user {
      field_name = "id"
      field_value = $employee.user_id
      output = ["name"]
    } as $user

    db.query attendance_punches {
      where = $db.attendance_punches.employees_id == $employee.id && $db.attendance_punches.work_date == $clock.work_date
      sort = {punched_at: "asc"}
      output = ["id", "punch_type", "punched_at", "schedule_snapshot"]
      return = {type: "list"}
    } as $confirmed_punches

    db.query attendance_punches {
      where = $db.attendance_punches.employees_id == $employee.id && $db.attendance_punches.work_date == $clock.work_date && $db.attendance_punches.punch_type == "entry"
      return = {type: "single"}
      output = ["schedule_snapshot"]
    } as $entry_snapshot

    var $schedule_snapshot {
      value = $entry_snapshot.schedule_snapshot ?? $schedule_day
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
    punches: $confirmed_punches
  }
  guid = "AUClfWGVS1Hui0CqPSturTlSZ4U"
}
