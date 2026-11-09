// Delete vacation_requests record.
query "vacation_requests/{vacation_requests_id}" verb=DELETE {
  api_group = "rh_api"
  auth = "user"

  input {
    int vacation_requests_id? filters=min:1
  }

  stack {
    function.run "RH API/authorize employee manager" {
      input = {authenticated_user_id: $auth.id}
    } as $authorization

    precondition (false) {
      error_type = "accessdenied"
      error = "A exclusão de solicitações de férias não está disponível."
    }
  }

  response = null
  guid = "tQAu7HqSRi_24fGh4d0rBlNfRzg"
}