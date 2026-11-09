// Edit vacation_requests record
query "vacation_requests/{vacation_requests_id}" verb=PATCH {
  api_group = "rh_api"
  auth = "user"

  input {
    int vacation_requests_id? filters=min:1
    text status filters=trim
  }

  stack {
    function.run "RH API/authorize employee manager" {
      input = {authenticated_user_id: $auth.id}
    } as $authorization

    precondition ($input.status == "Aprovada" || $input.status == "Rejeitada") {
      error_type = "badrequest"
      error = "Selecione uma decisão válida."
    }

    db.get vacation_requests {
      field_name = "id"
      field_value = $input.vacation_requests_id
      output = ["id", "status"]
    } as $vacation_request

    precondition ($vacation_request != null) {
      error_type = "notfound"
      error = "Solicitação de férias não encontrada."
    }

    precondition ($vacation_request.status == "Pendente") {
      error_type = "badrequest"
      error = "A solicitação já foi decidida."
    }

    db.patch vacation_requests {
      field_name = "id"
      field_value = $input.vacation_requests_id
      data = {
        status: $input.status
        decided_by: $auth.id
      }
    } as $vacation_requests
  }

  response = $vacation_requests
  guid = "TA_AXjgLT-tRtVFxdaY1MzmDhto"
}