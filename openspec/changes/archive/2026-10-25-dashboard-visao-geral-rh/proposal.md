# Proposal: Visão Geral Focada no Gestor de RH

## Why

A tela de "Visão Geral" (`/inicio`) continha cartões e informações voltadas para colaboradores comuns (como jornada de hoje, banco de horas, próximo turno e próximos eventos). Como o sistema é de uso exclusivo do Gestor de RH, o dashboard principal deve refletir métricas macro de gestão de pessoas.

## What

- Remover os cartões: "Próximo turno", "Banco de horas", "Férias", "Jornada de hoje" e "Próximos eventos".
- Adicionar os cartões gerenciais: "Total Colaboradores" e "Total Colaboradores em Férias", alimentados com dados reais do Xano.
- Atualizar a rota `/inicio` para carregar a listagem de colaboradores ao abrir (`on_load=State.load_employees`).
