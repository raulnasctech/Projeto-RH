function "RH API/validate work schedule" {
  input {
    json weekly_schedule
  }

  stack {
    precondition (
      $input.weekly_schedule.monday != null
      && $input.weekly_schedule.tuesday != null
      && $input.weekly_schedule.wednesday != null
      && $input.weekly_schedule.thursday != null
      && $input.weekly_schedule.friday != null
      && $input.weekly_schedule.saturday != null
      && $input.weekly_schedule.sunday != null
    ) {
      error_type = "badrequest"
      error = "Informe a configuração para os sete dias da semana."
    }

    function.run "RH API/validate work schedule day" {
      input = {
        is_workday: $input.weekly_schedule.monday.is_workday
        start_minute: $input.weekly_schedule.monday.start_minute
        end_minute: $input.weekly_schedule.monday.end_minute
        break_start_minute: $input.weekly_schedule.monday.break_start_minute
        break_end_minute: $input.weekly_schedule.monday.break_end_minute
      }
    } as $monday

    function.run "RH API/validate work schedule day" {
      input = {
        is_workday: $input.weekly_schedule.tuesday.is_workday
        start_minute: $input.weekly_schedule.tuesday.start_minute
        end_minute: $input.weekly_schedule.tuesday.end_minute
        break_start_minute: $input.weekly_schedule.tuesday.break_start_minute
        break_end_minute: $input.weekly_schedule.tuesday.break_end_minute
      }
    } as $tuesday

    function.run "RH API/validate work schedule day" {
      input = {
        is_workday: $input.weekly_schedule.wednesday.is_workday
        start_minute: $input.weekly_schedule.wednesday.start_minute
        end_minute: $input.weekly_schedule.wednesday.end_minute
        break_start_minute: $input.weekly_schedule.wednesday.break_start_minute
        break_end_minute: $input.weekly_schedule.wednesday.break_end_minute
      }
    } as $wednesday

    function.run "RH API/validate work schedule day" {
      input = {
        is_workday: $input.weekly_schedule.thursday.is_workday
        start_minute: $input.weekly_schedule.thursday.start_minute
        end_minute: $input.weekly_schedule.thursday.end_minute
        break_start_minute: $input.weekly_schedule.thursday.break_start_minute
        break_end_minute: $input.weekly_schedule.thursday.break_end_minute
      }
    } as $thursday

    function.run "RH API/validate work schedule day" {
      input = {
        is_workday: $input.weekly_schedule.friday.is_workday
        start_minute: $input.weekly_schedule.friday.start_minute
        end_minute: $input.weekly_schedule.friday.end_minute
        break_start_minute: $input.weekly_schedule.friday.break_start_minute
        break_end_minute: $input.weekly_schedule.friday.break_end_minute
      }
    } as $friday

    function.run "RH API/validate work schedule day" {
      input = {
        is_workday: $input.weekly_schedule.saturday.is_workday
        start_minute: $input.weekly_schedule.saturday.start_minute
        end_minute: $input.weekly_schedule.saturday.end_minute
        break_start_minute: $input.weekly_schedule.saturday.break_start_minute
        break_end_minute: $input.weekly_schedule.saturday.break_end_minute
      }
    } as $saturday

    function.run "RH API/validate work schedule day" {
      input = {
        is_workday: $input.weekly_schedule.sunday.is_workday
        start_minute: $input.weekly_schedule.sunday.start_minute
        end_minute: $input.weekly_schedule.sunday.end_minute
        break_start_minute: $input.weekly_schedule.sunday.break_start_minute
        break_end_minute: $input.weekly_schedule.sunday.break_end_minute
      }
    } as $sunday
  }

  response = {
    monday: {
      is_workday: $input.weekly_schedule.monday.is_workday
      start_minute: $input.weekly_schedule.monday.start_minute
      end_minute: $input.weekly_schedule.monday.end_minute
      break_start_minute: $input.weekly_schedule.monday.break_start_minute
      break_end_minute: $input.weekly_schedule.monday.break_end_minute
    }
    tuesday: {
      is_workday: $input.weekly_schedule.tuesday.is_workday
      start_minute: $input.weekly_schedule.tuesday.start_minute
      end_minute: $input.weekly_schedule.tuesday.end_minute
      break_start_minute: $input.weekly_schedule.tuesday.break_start_minute
      break_end_minute: $input.weekly_schedule.tuesday.break_end_minute
    }
    wednesday: {
      is_workday: $input.weekly_schedule.wednesday.is_workday
      start_minute: $input.weekly_schedule.wednesday.start_minute
      end_minute: $input.weekly_schedule.wednesday.end_minute
      break_start_minute: $input.weekly_schedule.wednesday.break_start_minute
      break_end_minute: $input.weekly_schedule.wednesday.break_end_minute
    }
    thursday: {
      is_workday: $input.weekly_schedule.thursday.is_workday
      start_minute: $input.weekly_schedule.thursday.start_minute
      end_minute: $input.weekly_schedule.thursday.end_minute
      break_start_minute: $input.weekly_schedule.thursday.break_start_minute
      break_end_minute: $input.weekly_schedule.thursday.break_end_minute
    }
    friday: {
      is_workday: $input.weekly_schedule.friday.is_workday
      start_minute: $input.weekly_schedule.friday.start_minute
      end_minute: $input.weekly_schedule.friday.end_minute
      break_start_minute: $input.weekly_schedule.friday.break_start_minute
      break_end_minute: $input.weekly_schedule.friday.break_end_minute
    }
    saturday: {
      is_workday: $input.weekly_schedule.saturday.is_workday
      start_minute: $input.weekly_schedule.saturday.start_minute
      end_minute: $input.weekly_schedule.saturday.end_minute
      break_start_minute: $input.weekly_schedule.saturday.break_start_minute
      break_end_minute: $input.weekly_schedule.saturday.break_end_minute
    }
    sunday: {
      is_workday: $input.weekly_schedule.sunday.is_workday
      start_minute: $input.weekly_schedule.sunday.start_minute
      end_minute: $input.weekly_schedule.sunday.end_minute
      break_start_minute: $input.weekly_schedule.sunday.break_start_minute
      break_end_minute: $input.weekly_schedule.sunday.break_end_minute
    }
  }
  guid = "5-1oLy_t2J8bjv5GWyaBE63fM4k"
}
