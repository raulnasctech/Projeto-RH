// Get a collaborator's weekly work schedule
query "work_schedules/{employees_id}" verb=GET {
  api_group = "rh_api"
  auth = "user"

  input {
    int employees_id? filters=min:1
  }

  stack {
    function.run "RH API/authorize employee manager" {
      input = {authenticated_user_id: $auth.id}
    } as $authorization

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
      output = ["id", "employees_id", "weekly_schedule"]
    } as $work_schedule
  }

  response = $work_schedule
  guid = "CGvAsv5wb4oHO3zwYsQmuSH8BF0"
}
