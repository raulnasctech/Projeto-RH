# Proposal

## Why

A página de gestão de colaboradores apresenta um número demonstrativo de colaboradores ativos, que pode divergir dos registros reais. O card de pendências também ocupa espaço com uma contagem não conectada a dados reais, embora não faça parte do resumo desejado.

## What Changes

- Calcular o indicador “Colaboradores ativos” a partir dos colaboradores retornados pela API, contando registros com situação “Ativo”.
- Garantir que a consulta de colaboradores inclua registros sem conta de acesso, para que continuem visíveis após recarregar a página e sejam contados corretamente.
- Atualizar o indicador após o carregamento e após o cadastro confirmado de um novo colaborador.
- Remover o card de “Pendências” da página de gestão de colaboradores.
- Preservar o card “Em férias” e o restante da tela sem mudanças nesta alteração.
- Fora do escopo: criar um total geral de colaboradores, implementar contagem de férias ou solicitações, ou alterar endpoints e permissões da API.

## Capabilities

### New Capabilities

- `employee-dashboard`: apresentar o indicador real de colaboradores ativos e remover o card de pendências da página de gestão.

### Modified Capabilities

## Impact

- Página Reflex de gestão de colaboradores e estado compartilhado da listagem real.
- Testes do estado e da composição da página de colaboradores.
- API Xano de listagem: incluir colaboradores sem conta associada mantendo a compatibilidade com nomes de contas legados.
- O contador reutiliza a listagem já protegida de colaboradores.
