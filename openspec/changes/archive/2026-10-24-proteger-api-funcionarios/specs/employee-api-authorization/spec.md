# Spec Delta

## Purpose

Esta capacidade define como a API de funcionários valida a identidade e o perfil RH no backend antes de permitir acesso a dados pessoais ou operações de cadastro.

## ADDED Requirements

### Requirement: Endpoints de funcionários exigem autenticação
A API MUST exigir um token válido de usuário para listar, consultar, cadastrar, editar ou excluir funcionários. Chamadas sem token válido MUST ser rejeitadas antes de acessar ou alterar registros.

#### Scenario: Chamada sem token válido
- **WHEN** um cliente chama qualquer endpoint de funcionários sem token válido
- **THEN** a API rejeita a chamada como não autenticada e não retorna nem altera dados de funcionários

### Requirement: Operações de funcionários exigem perfil Gestor RH
A API MUST autorizar operações de funcionários somente quando o registro da tabela `user` identificado pelo token válido tiver `role` exatamente igual a `Gestor RH`. Essa autorização MUST ser aplicada a listagem, consulta individual, cadastro, edição e exclusão, independentemente da interface usada para chamar a API. O cadastro público MUST NOT permitir que o solicitante escolha ou altere seu próprio perfil.

#### Scenario: Usuário autenticado com perfil Gestor RH
- **WHEN** o token é válido e o registro autenticado em `user` tem `role` igual a `Gestor RH`
- **THEN** a API permite a operação solicitada sobre funcionários

#### Scenario: Usuário autenticado com outro perfil
- **WHEN** o token é válido e o registro autenticado em `user` tem outro valor de `role` ou não tem perfil definido
- **THEN** a API rejeita a operação como não autorizada e não retorna nem altera dados de funcionários

#### Scenario: Registro autenticado não encontrado
- **WHEN** a identidade do token não pode ser resolvida para um registro em `user`
- **THEN** a API rejeita a operação como não autorizada e não retorna nem altera dados de funcionários
