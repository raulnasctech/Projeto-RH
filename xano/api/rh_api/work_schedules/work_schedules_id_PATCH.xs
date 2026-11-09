// Replace a collaborator's complete weekly work schedule
query "work_schedules/{work_schedules_id}" verb=PATCH {
  api_group = "rh_api"
  auth = "user"

  input {
    int work_schedules_id? filters=min:1
    json weekly_schedule
  }

  stack {
    function.run "RH API/authorize employee manager" {
      input = {authenticated_user_id: $auth.id}
    } as $authorization

    function.run "RH API/validate work schedule" {
      input = {weekly_schedule: $input.weekly_schedule}
    } as $validated_schedule

    db.get work_schedules {
      field_name = "id"
      field_value = $input.work_schedules_id
      output = ["id"]
    } as $existing_schedule

    precondition ($existing_schedule != null) {
      error_type = "notfound"
      error = "A jornada do colaborador não foi encontrada."
    }

    db.patch work_schedules {
      field_name = "id"
      field_value = $input.work_schedules_id
      data = {
        weekly_schedule: $validated_schedule
      }
    } as $work_schedule
  }

  response = $work_schedule
  guid = "2ttiRerKK2DMUe7KUMcLZ7uNhIY"
}
