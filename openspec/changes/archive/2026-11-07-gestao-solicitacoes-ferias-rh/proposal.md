# Proposal

## Why

O sistema ainda não oferece ao Gestor RH um fluxo para registrar e decidir solicitações de férias, e a tabela `vacation_requests` não está disponível no Xano conforme informado. Com isso, não há uma fonte confiável para acompanhar os períodos aprovados nem para calcular o indicador de colaboradores atualmente em férias.

## What Changes

- Criar ou restaurar no Xano a tabela `vacation_requests`, relacionada a `employees` e à tabela de autenticação `user`, para persistir colaborador, período, situação e responsável pela decisão.
- Adicionar ao sistema um fluxo exclusivo do Gestor RH para registrar solicitações em nome de colaboradores e listar, aprovar ou rejeitar solicitações pendentes.
- Validar período e situação no backend, impedir decisões sobre solicitações que não estejam pendentes e proteger todos os endpoints de férias com autenticação e autorização Gestor RH.
- Atualizar o indicador de colaboradores em férias para contar colaboradores com solicitações aprovadas cujo período inclui a data atual.

Fora do escopo: portal de autoatendimento para funcionários, cancelamento de solicitações, regras de saldo/direito a férias, integração com folha de pagamento e recuperação de registros que tenham sido apagados do Xano.

## Capabilities

### New Capabilities

- `vacation-request-management`: criação/restauração da tabela no Xano e gestão de solicitações de férias pelo Gestor RH, incluindo atualização do indicador de férias.

### Modified Capabilities

Nenhuma.

## Impact

- Interface Reflex: nova área de gestão de férias, formulário de solicitação em nome do colaborador, listagem e ações de decisão; indicador do painel atualizado.
- Serviços e testes Python do app: integração autenticada com os endpoints de férias e estados de carregamento, vazio e erro.
- Xano: tabela `vacation_requests` e endpoints de consulta, criação e decisão; autorização aplicada no backend para o perfil `Gestor RH`.
- O schema local existente referencia `users` em `approved_by`, enquanto a autenticação e o relacionamento dos funcionários usam `user`; a especificação e a implementação deverão usar a tabela real `user`.
