// Query all users records
query users verb=GET {
  api_group = "rh_api"

  input {
  }

  stack {
    db.query users {
      return = {type: "list"}
    } as $users
  }

  response = $users
  guid = "fExTcOVJkrpFuRIM2BT4FAOD6sE"
}