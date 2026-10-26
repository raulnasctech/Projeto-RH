# Spec Delta

## Purpose

Definir como usuários RH mantêm departamentos e associam funcionários a departamentos e cargos, preservando a consistência entre os cadastros.

## ADDED Requirements

### Requirement: Consulta de departamentos
O sistema MUST apresentar os departamentos persistidos no backend e MUST distinguir carregamento, resultado vazio e falha de consulta.

#### Scenario: Consulta concluída com departamentos
- **WHEN** um usuário autorizado abre a área de departamentos e o backend retorna registros
- **THEN** o sistema apresenta os departamentos retornados pelo backend

#### Scenario: Consulta sem departamentos
- **WHEN** uma consulta válida não encontra departamentos
- **THEN** o sistema informa que não há departamentos cadastrados

### Requirement: Manutenção de departamentos
O sistema MUST permitir que usuários com perfil RH criem e editem departamentos com os dados aceitos pelo backend e MUST informar sucesso ou falha de persistência.

#### Scenario: Cadastro ou edição de departamento
- **WHEN** um usuário RH envia dados válidos de um departamento
- **THEN** o backend persiste os dados e o sistema apresenta a confirmação correspondente

#### Scenario: Operação não autorizada em departamento
- **WHEN** um usuário sem perfil RH tenta criar ou editar um departamento
- **THEN** o backend rejeita a operação e os dados permanecem inalterados

### Requirement: Associação de funcionário a departamento e cargo
O sistema MUST permitir que usuários RH associem um funcionário a um departamento existente e informem seu cargo nos dados do funcionário. O sistema MUST informar quando o departamento selecionado não puder ser associado.

#### Scenario: Associação válida
- **WHEN** um usuário RH salva um funcionário com um departamento existente e um cargo válido
- **THEN** o backend persiste a associação e a interface apresenta os dados associados

#### Scenario: Departamento inválido ou indisponível
- **WHEN** um usuário RH tenta salvar um funcionário com uma associação de departamento inválida
- **THEN** o backend rejeita a associação e o sistema informa que o cadastro não foi concluído
