// Get departments record
query "departments/{departments_id}" verb=GET {
  api_group = "rh_api"

  input {
    int departments_id? filters=min:1
  }

  stack {
    db.get departments {
      field_name = "id"
      field_value = $input.departments_id
    } as $departments
  
    precondition ($departments != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $departments
  guid = "YdQuFe4uYg2duBpaTnWWziDGpdY"
}