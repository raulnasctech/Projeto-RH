# Proposal

## Why

Atualmente, o sistema permite apenas o cadastro e a listagem de colaboradores. Não há uma forma de corrigir erros de digitação, atualizar informações funcionais (como promoções ou mudanças de departamento) ou inativar colaboradores que saíram da empresa através da interface. Esta mudança é necessária para completar o ciclo de vida básico do colaborador no sistema.

## What Changes

- **Visualização Detalhada**: Adição de uma página ou modal de detalhes para cada colaborador, exibindo todas as informações funcionais.
- **Edição de Dados**: Funcionalidade para editar Nome, Cargo e Departamento de colaboradores existentes.
- **Gestão de Status**: Possibilidade de alterar o status do colaborador (ex: de "Ativo" para "Inativo").
- **Proteção de Escrita**: Garantia de que apenas usuários com perfil "Gestor RH" possam realizar essas alterações.

## Capabilities

### New Capabilities
- `employee-details`: Visualização detalhada de um único colaborador e seu histórico básico.

### Modified Capabilities
- `employee-management`: Adição de requisitos para atualização (PATCH) de colaboradores e transição de estados (status).

## Impact

- **API Xano**: Novo endpoint `PATCH /employees/{id}` e possivelmente `GET /employees/{id}`.
- **Frontend Reflex**: Atualização da tabela de diretório para incluir ações (links/botões), criação de nova página/modal de edição e integração com os novos endpoints.
- **Segurança**: Reforço das permissões de Gestor RH para operações de escrita.
