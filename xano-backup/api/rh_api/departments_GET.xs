// Query all departments records
query departments verb=GET {
  api_group = "rh_api"

  input {
  }

  stack {
    db.query departments {
      return = {type: "list"}
    } as $departments
  }

  response = $departments
  guid = "11nVvQmpC977K7RN3dm54c3OV94"
}