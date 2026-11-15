// Resolve the current operational date and time in the RH workspace timezone
function "RH API/get attendance clock" {
  input {
  }

  stack {
    var $server_now {
      value = now
    }

    var $work_date {
      value = $server_now|format_timestamp:"Y-m-d":"America/Sao_Paulo"
    }

    var $weekday_number {
      value = $server_now|format_timestamp:"N":"America/Sao_Paulo"|to_int
    }

    var $weekday_keys {
      value = {
        1: "monday"
        2: "tuesday"
        3: "wednesday"
        4: "thursday"
        5: "friday"
        6: "saturday"
        7: "sunday"
      }
    }

    var $weekday {
      value = $weekday_keys|get:$weekday_number
    }

    var $hour {
      value = $server_now|format_timestamp:"G":"America/Sao_Paulo"|to_int
    }

    var $minute {
      value = $server_now|format_timestamp:"i":"America/Sao_Paulo"|to_int
    }

    var $current_minute {
      value = ($hour * 60) + $minute
    }
  }

  response = {
    server_now: $server_now
    work_date: $work_date
    weekday: $weekday
    current_minute: $current_minute
  }
  guid = "-AFIXSXYJxPoblsInxBvfv_8WyM"
}
