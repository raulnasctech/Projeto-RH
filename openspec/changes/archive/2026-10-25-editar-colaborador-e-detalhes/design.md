# Design

## Context

O sistema atual possui endpoints para cadastro (`POST /employees`) e listagem (`GET /employees`). A estrutura de dados no Xano já suporta campos como `name`, `job_title`, `admissao`, `status` e relações com `users` e `departments`. O frontend em Reflex utiliza um `employee_service.py` para comunicação com a API. Veja `proposal.md` para a motivação completa.

## Goals / Non-Goals

**Goals:**
- Implementar edição de colaboradores existentes via `PATCH`.
- Implementar visualização detalhada de um colaborador via `GET /employees/{id}`.
- Permitir alteração de `status` (Ativo/Inativo).
- Adicionar navegação da listagem para os detalhes/edição.

**Non-Goals:**
- Edição de histórico de ponto ou férias (ficará para mudanças futuras).
- Exclusão física de registros (apenas inativação lógica via status).
- Criação de novos departamentos ou usuários nesta interface (escopo de outras telas).

## Decisions

- **Visualização: Modal vs. Página**: Utilizaremos um **Modal** para edição rápida e uma **Página** para visualização detalhada. O Modal evita perda de contexto na listagem, enquanto a página permite futuras expansões de abas (férias, histórico).
- **Método de Atualização**: Usaremos `PATCH` em vez de `PUT`. O Xano lida bem com `PATCH` para atualizações parciais, o que simplifica o envio apenas dos campos alterados.
- **Identificação**: O identificador do colaborador será passado via URL (path parameter) tanto na API quanto no roteamento do Reflex.
- **Validação de Perfil**: A validação continuará sendo feita no Backend. O Frontend apenas ocultará os botões de ação se o perfil não for `Gestor RH`, mas a API rejeitará qualquer tentativa não autorizada.

## Risks / Trade-offs

- **[Risco] Inconsistência de Dados**: Alterar o departamento de um colaborador pode afetar relatórios históricos. → **Mitigação**: O sistema apenas altera o vínculo atual; se for necessário histórico real, precisaremos de uma tabela de histórico funcional no futuro.
- **[Risco] Concorrência**: Dois gestores editando o mesmo colaborador simultaneamente. → **Mitigação**: Como o volume de usuários RH é baixo, o risco é aceitável para o MVP. O último a salvar sobrescreve.

## Migration Plan

1.  **Backend (Xano)**:
    - Criar endpoint `GET /employees/{id}` (autorizado).
    - Criar endpoint `PATCH /employees/{id}` (autorizado para RH).
2.  **Frontend (Service Layer)**:
    - Adicionar `get_employee(id)` ao `employee_service.py`.
    - Adicionar `update_employee(id, data)` ao `employee_service.py`.
3.  **Frontend (UI)**:
    - Modificar a tabela em `Gestao_RH_Impacta.py` para incluir o botão de ações.
    - Criar componente de detalhes/edição.
