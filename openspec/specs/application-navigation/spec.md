# application-navigation Specification

## Purpose

Define quais opções e informações auxiliares são exibidas nas barras laterais da aplicação, mantendo a navegação consistente entre o início e as páginas internas.

## Requirements

### Requirement: Barra lateral sem atalho para Perfil
A barra lateral da aplicação MUST NOT exibir a opção “Perfil” como item de navegação. A remoção do atalho MUST NOT impedir o acesso direto à rota `/perfil`, que continua sujeita às regras de autenticação existentes.

#### Scenario: Usuário navega pelo menu lateral
- **WHEN** o usuário visualiza a barra lateral no início ou em uma página interna
- **THEN** a opção “Perfil” não é apresentada entre os itens do menu

#### Scenario: Usuário acessa diretamente a página de perfil
- **WHEN** um usuário autenticado navega diretamente para `/perfil`
- **THEN** a aplicação mantém o comportamento de acesso já definido para essa rota

### Requirement: Barra lateral sem cartão de ajuda de RH
A barra lateral da aplicação MUST NOT exibir cartões ou mensagens que solicitem contato com o RH, incluindo variações com os textos “Precisa de ajuda?”, “Fale com o RH” ou “Suporte RH”.

#### Scenario: Usuário visualiza a barra lateral
- **WHEN** a barra lateral é exibida no início ou em uma página interna
- **THEN** nenhum cartão ou mensagem de ajuda que solicite contato com o RH é apresentado
