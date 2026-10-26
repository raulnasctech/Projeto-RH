# Proposal

## Why

A aplicação já autentica usuários pelo Xano, mas mantém o token e o nome do usuário em `LocalStorage`, acessível ao navegador. A mudança estabelece uma sessão segura para o fluxo de acesso existente e impede que páginas internas sejam usadas sem autenticação válida.

## What Changes

- Manter o login e o cadastro existentes conectados ao Xano, sem alterar as regras de criação de contas.
- Guardar o token e a identidade em contexto de sessão no servidor, sem expor o token ao navegador ou registrá-lo em logs.
- Exigir sessão válida para acessar as páginas internas e limpar a sessão ao sair ou quando o Xano rejeitar/expirar o token.
- Apresentar falhas de autenticação e de consulta de identidade sem iniciar uma sessão inválida.

Fora do escopo: autorização de operações de cadastro de RH no Xano, gestão de funcionários ou departamentos e alterações visuais das telas.

## Capabilities

### New Capabilities

- `authentication`: autenticação existente com sessão protegida, controle de acesso às páginas internas, logout e tratamento de sessão expirada.

### Modified Capabilities

Nenhuma. O projeto ainda não possui especificações principais registradas.

## Impact

- `Gestao_RH_Impacta/Gestao_RH_Impacta.py`: estado Reflex, chamadas aos endpoints `/auth/login`, `/auth/signup` e `/auth/me`, logout e páginas internas.
- Xano: contratos existentes de autenticação e consulta de identidade; não estão previstas alterações nos endpoints nesta mudança.
- Testes: cobertura dos fluxos válidos, inválidos, expiração da sessão e acesso às páginas internas.
