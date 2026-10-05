// Add PAPEL record
query papel verb=POST {
  api_group = "Event Logs"

  input {
    dblink {
      table = "PAPEL"
    }
  }

  stack {
    db.add PAPEL {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $papel
  }

  response = $papel
  guid = "QnlVRNS4SMKDX6itVLAr5zMYw6I"
}