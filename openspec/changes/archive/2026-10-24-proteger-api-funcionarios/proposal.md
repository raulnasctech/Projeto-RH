# Proposal

## Why

Os endpoints Xano de funcionários estão sem autenticação e autorização, inclusive operações que expõem salário e permitem alterar ou excluir cadastros. A proteção apenas nas páginas Reflex não impede chamadas diretas à API; por isso, o próprio backend precisa verificar a identidade e o perfil RH.

## What Changes

- Exigir token válido e perfil `Gestor RH` para listar, consultar, cadastrar, editar ou excluir funcionários.
- Validar o perfil diretamente no registro autenticado da tabela `user`, usando o campo `role` com valor exatamente igual a `Gestor RH`.
- Rejeitar chamadas sem autenticação ou sem autorização diretamente nos endpoints Xano.
- Não permitir que o cadastro público escolha ou atribua perfil; a atribuição de `Gestor RH` é administrativa.
- Manter fora do escopo os endpoints de departamentos, a gestão/provisionamento de perfis e alterações na interface Reflex.

## Capabilities

### New Capabilities

- `employee-api-authorization`: autorização no backend para operações da API de funcionários.

### Modified Capabilities

Nenhuma. A spec de autenticação existente cobre sessões e páginas Reflex, não autorização de operações da API de funcionários.

## Impact

- Endpoints Xano `employees` (GET e POST) e `employees/{employees_id}` (GET, PATCH e DELETE).
- Campo `role` da tabela Xano `user`, que é a mesma tabela usada pela autenticação.
- Nenhuma dependência ou alteração na interface Reflex prevista.
