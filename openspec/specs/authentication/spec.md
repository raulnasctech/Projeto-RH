# authentication Specification

## Purpose

Define como usuários autenticam-se no sistema e mantêm uma sessão individual, protegida e limitada às páginas internas enquanto as credenciais continuam válidas.

## Requirements

### Requirement: Sessão após autenticação válida
O sistema MUST iniciar uma sessão somente quando o Xano confirmar a autenticação e retornar uma identidade válida. O token de acesso MUST permanecer no servidor e MUST NOT ser enviado ao navegador, persistido no armazenamento do navegador ou registrado em logs. O fluxo existente de login e cadastro MUST continuar disponível.

#### Scenario: Login ou cadastro confirmado pelo Xano
- **WHEN** o Xano confirma o login ou o cadastro e retorna uma identidade válida
- **THEN** o sistema inicia uma sessão para aquele usuário, mantém o token somente no servidor e encaminha o usuário para a área interna

#### Scenario: Credenciais, resposta ou identidade inválidas
- **WHEN** as credenciais são rejeitadas, a resposta não contém os dados necessários ou a consulta de identidade falha
- **THEN** o sistema não inicia uma sessão, informa que o acesso não foi concluído e não expõe o token

### Requirement: Acesso autenticado às páginas internas
O sistema MUST exigir uma sessão autenticada para apresentar as páginas internas da aplicação. Uma navegação direta para uma página interna sem sessão MUST retornar o usuário à tela de acesso.

#### Scenario: Usuário autenticado abre uma página interna
- **WHEN** um usuário com sessão válida abre uma página interna
- **THEN** o sistema apresenta a página solicitada

#### Scenario: Usuário sem sessão abre uma página interna
- **WHEN** um usuário sem sessão válida navega diretamente para uma página interna
- **THEN** o sistema não apresenta o conteúdo interno e redireciona para a tela de acesso

### Requirement: Encerramento e rejeição da sessão
O sistema MUST limpar os dados da sessão quando o usuário solicita logout ou quando uma chamada autenticada ao Xano informa que o token expirou ou foi rejeitado. Depois disso, o acesso às páginas internas MUST exigir nova autenticação.

#### Scenario: Usuário solicita logout
- **WHEN** um usuário autenticado solicita sair
- **THEN** o sistema invalida a sessão local e retorna à tela de acesso

#### Scenario: Xano rejeita um token expirado ou inválido
- **WHEN** uma chamada autenticada ao Xano retorna uma resposta que indica token expirado ou inválido
- **THEN** o sistema limpa a sessão e solicita nova autenticação
