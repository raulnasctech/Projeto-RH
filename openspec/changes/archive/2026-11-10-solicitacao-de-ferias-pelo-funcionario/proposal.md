# Proposal

## Why

Atualmente, somente o Gestor RH consegue iniciar uma solicitação de férias, em nome de um funcionário. O funcionário precisa de um fluxo próprio para informar o período desejado e acompanhar se o pedido está pendente, aprovado ou rejeitado, enquanto o RH mantém o controle da decisão.

## What Changes

- Permitir que um funcionário autenticado solicite férias informando as datas de início e fim.
- Restringir no backend a criação e a consulta do funcionário às solicitações vinculadas ao seu próprio cadastro.
- Exibir os pedidos dos funcionários na gestão de férias do Gestor RH, mantendo as ações de aprovar e rejeitar somente para esse perfil.
- Disponibilizar ao funcionário a consulta do período solicitado e do status atualizado após a decisão do RH.
- Manter o cadastro de solicitação em nome de funcionário já disponível ao Gestor RH, além do novo fluxo iniciado pelo funcionário.
- Manter os status existentes (`Pendente`, `Aprovada` e `Rejeitada`) e impedir decisões repetidas.

Fora do escopo: cancelamento ou edição de pedidos pelo funcionário; regras de saldo de férias, sobreposição de períodos ou validação de datas passadas; notificações ao funcionário; alteração do indicador de funcionários atualmente em férias.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `vacation-request-management`: permitir solicitação e consulta de férias pelo próprio funcionário, com isolamento por identidade autenticada, preservando a administração e decisão pelo Gestor RH.

## Impact

- Interface Reflex de férias do funcionário e interface existente do Gestor RH.
- Estado e serviço Python de solicitações de férias, incluindo autenticação Bearer e tratamento dos novos contratos.
- Endpoints Xano de férias para permitir operações específicas por perfil e vínculo, sem expor pedidos de outros funcionários ou permitir decisões por funcionários.
- Testes de serviço, estado e contratos Xano; documentação OpenSpec da capability `vacation-request-management`.
