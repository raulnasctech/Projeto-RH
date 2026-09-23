// Add New OR Get Exist PEDIDO record
query addorgetpedido verb=POST {
  api_group = "addorgetpedido"
  auth = "user"

  input {
  }

  stack {
    db.get user {
      field_name = "user_id"
      field_value = $auth.id
    } as $user_logado
  
    db.get STATUS_PEDIDO {
      field_name = "status"
      field_value = "Criado"
    } as $STATUS_PEDIDO_Criado
  
    db.query PEDIDO {
      where = $db.PEDIDO.user_id == $user_logado.id && $db.PEDIDO.status_pedido_id == $STATUS_PEDIDO_Criado.id
      return = {type: "single"}
    } as $pedido_aberto
  
    conditional {
      if ($pedido_aberto == null) {
        db.add PEDIDO {
          enforce_hidden_fields = false
          data = {
            created_at      : "now"
            total           : 0
            nfc_e           : null
            cod_entrega     : null
            cliente_id      : $cliente_logado.id
            status_pedido_id: $STATUS_PEDIDO_Criado.id
          }
        } as $pedido_aberto
      }
    
      elseif () {
      }
    }
  }

  response = $pedido_aberto
  tags = ["pedido"]
  guid = "HE--6jtCvqiLBkcOhilerDEBmt4"
}