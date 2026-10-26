# employee-management Specification

## Purpose

Definir o cadastro e a gestão (atualização e status) de funcionários pelo RH.

## Requirements

### Requirement: Cadastro e edição de funcionário
O sistema MUST permitir que um usuário com perfil Gestor RH cadastre um funcionário informando seu nome, selecionando uma conta de acesso existente ainda não vinculada e selecionando um departamento existente. O backend MUST persistir o identificador da conta em `user_id`, validar que a conta existe e impedir que a mesma conta seja vinculada a mais de um funcionário. Cargo e data de admissão podem ser informados; a situação inicial MUST ser “Ativo”. O formulário MUST NOT solicitar nem enviar salário. Após a confirmação do backend, o funcionário MUST aparecer na listagem real de colaboradores. Além do cadastro, o sistema MUST permitir a atualização (edição) de um funcionário existente, possibilitando alterar nome, cargo, departamento e situação (status).

#### Scenario: Cadastro válido com conta existente
- **WHEN** um usuário Gestor RH informa o nome do funcionário, seleciona uma conta ainda não vinculada e um departamento existente e envia os dados funcionais válidos
- **THEN** o backend persiste o registro com o `user_id` selecionado e a listagem apresenta o novo funcionário após o cadastro e após recarregar a página

#### Scenario: Edição válida de colaborador
- **WHEN** um usuário Gestor RH altera o nome, cargo ou departamento de um colaborador existente e salva as alterações
- **THEN** o backend atualiza os dados e a interface reflete as mudanças imediatamente

#### Scenario: Alteração de status (Inativação)
- **WHEN** um usuário Gestor RH altera a situação de um colaborador de "Ativo" para "Inativo"
- **THEN** o backend persiste a mudança e o colaborador passa a ser exibido com o novo status no diretório

#### Scenario: Conta já vinculada ou inexistente
- **WHEN** o cadastro ou edição referencia uma conta inexistente, a própria conta do Gestor RH ou uma conta já vinculada a outro funcionário
- **THEN** o backend rejeita a operação sem criar um vínculo duplicado ou registro parcial

#### Scenario: Nome ou departamento inválido
- **WHEN** o nome está vazio ou o departamento selecionado não existe durante o cadastro ou edição
- **THEN** o backend rejeita a alteração, não persiste dados parciais e a interface informa o problema

#### Scenario: Usuário sem perfil Gestor RH
- **WHEN** um usuário sem perfil Gestor RH tenta cadastrar ou editar um funcionário
- **THEN** o backend rejeita a operação e nenhum dado é criado ou alterado

### Requirement: Opções protegidas de contas e departamentos
O backend MUST fornecer contas existentes ainda não vinculadas e departamentos existentes para o formulário somente a usuários autenticados com perfil Gestor RH. A resposta MUST conter apenas os identificadores e nomes necessários à seleção, sem credenciais ou dados pessoais desnecessários.
