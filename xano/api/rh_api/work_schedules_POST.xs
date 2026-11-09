// Create a collaborator's weekly work schedule
query work_schedules verb=POST {
  api_group = "rh_api"
  auth = "user"

  input {
    int employees_id filters=min:1
    json weekly_schedule
  }

  stack {
    function.run "RH API/authorize employee manager" {
      input = {authenticated_user_id: $auth.id}
    } as $authorization

    function.run "RH API/validate work schedule" {
      input = {weekly_schedule: $input.weekly_schedule}
    } as $validated_schedule

    db.get employees {
      field_name = "id"
      field_value = $input.employees_id
      output = ["id"]
    } as $employee

    precondition ($employee != null) {
      error_type = "notfound"
      error = "O colaborador selecionado não está disponível."
    }

    db.get work_schedules {
      field_name = "employees_id"
      field_value = $input.employees_id
      output = ["id"]
    } as $existing_schedule

    precondition ($existing_schedule == null) {
      error_type = "badrequest"
      error = "O colaborador já possui uma jornada cadastrada."
    }

    db.add work_schedules {
      data = {
        employees_id: $input.employees_id
        weekly_schedule: $validated_schedule
      }
    } as $work_schedule
  }

  response = $work_schedule
  guid = "qN5yipWTZPW9SoFhPc5ImeUwYJM"
}
