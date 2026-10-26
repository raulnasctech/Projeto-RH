// Add employees record
query employees verb=POST {
  api_group = "rh_api"
  auth = "user"

  input {
    text name filters=trim
    int user_id filters=min:1
    int departaments_id filters=min:1
    text job_title? filters=trim
    date admissao?
  }

  stack {
    function.run "RH API/authorize employee manager" {
      input = {authenticated_user_id: $auth.id}
    } as $authorization

    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $input

    precondition ($input.name != "") {
      error_type = "badrequest"
      error = "Informe o nome do funcionário."
    }

    db.get user {
      field_name = "id"
      field_value = $input.user_id
      output = ["id"]
    } as $selected_user

    precondition ($selected_user != null && $selected_user.id != $auth.id) {
      error_type = "badrequest"
      error = "Selecione uma conta existente válida."
    }

    db.query employees {
      where = $db.employees.user_id == $input.user_id
      return = {type: "single"}
      output = ["id"]
    } as $linked_employee

    precondition ($linked_employee == null) {
      error_type = "badrequest"
      error = "Esta conta já está vinculada a um colaborador."
    }

    db.get departaments {
      field_name = "id"
      field_value = $input.departaments_id
      output = ["id"]
    } as $selected_department

    precondition ($selected_department != null) {
      error_type = "notfound"
      error = "O departamento selecionado não está disponível."
    }

    db.add employees {
      data = {
        created_at: "now"
        user_id: $input.user_id
        name: $input.name
        departaments_id: $input.departaments_id
        job_title: $input.job_title
        admissao: $input.admissao
        status: "Ativo"
      }
    } as $employees
  }

  response = $employees
  guid = "uYojWHLYm6YypAl-0IYbC2EZPXk"
}