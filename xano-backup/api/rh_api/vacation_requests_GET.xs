// Query all vacation_requests records
query vacation_requests verb=GET {
  api_group = "rh_api"

  input {
  }

  stack {
    db.query vacation_requests {
      return = {type: "list"}
    } as $vacation_requests
  }

  response = $vacation_requests
  guid = "0MbYWxE5wGusg1gHiLdva--U2m4"
}