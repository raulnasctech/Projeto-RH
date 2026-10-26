# Design: Visão Geral Focada no Gestor de RH

## Architecture

- **Frontend (Reflex):**
  - Refatorar a função `dashboard()` em `Gestao_RH_Impacta.py`.
  - Configurar `on_load=State.load_employees` em `/inicio`.
  - Exibir dois cartões principais no topo: Total de Colaboradores e Total de Colaboradores em Férias.
  - Remover componentes de jornada, eventos e ponto eletrônico de funcionário.
