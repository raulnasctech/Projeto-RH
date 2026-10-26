# Spec Delta

## Purpose

Define como usuários administrativos autenticam-se e como o sistema limita operações de RH às pessoas autorizadas, mantendo a decisão de acesso no backend.

## ADDED Requirements

### Requirement: Autenticação de usuários administrativos
O sistema MUST permitir que um usuário administrativo envie credenciais válidas ao serviço de autenticação e estabeleça uma sessão associada à sua identidade e perfil. Credenciais inválidas ou falhas do serviço MUST ser apresentadas sem iniciar uma sessão.

#### Scenario: Login com credenciais válidas
- **WHEN** um usuário envia credenciais válidas
- **THEN** o sistema inicia uma sessão autenticada e apresenta a área administrativa

#### Scenario: Login com credenciais inválidas
- **WHEN** um usuário envia credenciais inválidas
- **THEN** o sistema informa que o acesso não foi concluído e não inicia uma sessão autenticada

### Requirement: Autorização de operações administrativas
O backend MUST autorizar cada operação de criação, edição ou desativação de cadastros de RH somente quando a sessão autenticada tiver o perfil RH. A autorização de cada operação MUST ser validada no backend; o estado da interface não é uma barreira de segurança.

#### Scenario: Usuário RH executa uma operação administrativa
- **WHEN** um usuário autenticado com perfil RH envia uma operação autorizada
- **THEN** o backend valida o perfil e processa a operação

#### Scenario: Usuário sem perfil RH tenta alterar um cadastro
- **WHEN** um usuário sem perfil RH tenta criar, editar ou desativar um cadastro de RH
- **THEN** o backend rejeita a operação e os dados permanecem inalterados

### Requirement: Encerramento da sessão
O sistema MUST encerrar a sessão administrativa quando o usuário solicita logout e MUST exigir nova autenticação quando a sessão expira ou é rejeitada pelo serviço.

#### Scenario: Logout solicitado
- **WHEN** um usuário autenticado solicita sair
- **THEN** a sessão deixa de autorizar operações administrativas e a interface retorna à tela de acesso

#### Scenario: Sessão expirada
- **WHEN** uma operação recebe uma resposta de sessão expirada ou inválida
- **THEN** o sistema encerra a sessão local e solicita nova autenticação
