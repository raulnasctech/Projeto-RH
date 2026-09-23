// Delete Colaboradores record.
query "colaboradores/{colaboradores_id}" verb=DELETE {
  api_group = "Event Logs"

  input {
    int colaboradores_id? filters=min:1
  }

  stack {
    db.del Colaboradores {
      field_name = "id"
      field_value = $input.colaboradores_id
    }
  }

  response = null
  guid = "RBqfgx9QrdPe9HPF2i6ggH4RCzc"
}