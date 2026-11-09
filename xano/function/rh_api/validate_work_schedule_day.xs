function "RH API/validate work schedule day" {
  input {
    bool is_workday
    int? start_minute
    int? end_minute
    int? break_start_minute
    int? break_end_minute
  }

  stack {
    precondition (
      (
        $input.is_workday == true
        && $input.start_minute != null
        && $input.end_minute != null
        && $input.start_minute >= 0
        && $input.start_minute < 1440
        && $input.end_minute > $input.start_minute
        && $input.end_minute < 1440
        && $input.break_start_minute == null
        && $input.break_end_minute == null
      )
      || (
        $input.is_workday == true
        && $input.start_minute != null
        && $input.end_minute != null
        && $input.start_minute >= 0
        && $input.start_minute < 1440
        && $input.end_minute > $input.start_minute
        && $input.end_minute < 1440
        && $input.break_start_minute > $input.start_minute
        && $input.break_end_minute > $input.break_start_minute
        && $input.break_end_minute < $input.end_minute
      )
      || (
        $input.is_workday == false
        && $input.start_minute == null
        && $input.end_minute == null
        && $input.break_start_minute == null
        && $input.break_end_minute == null
      )
    ) {
      error_type = "badrequest"
      error = "A jornada contém horários incompletos ou fora de ordem."
    }
  }

  response = null
  guid = "r0y_0bdAsJjor8DZ36hzqLZ6gH0"
}
