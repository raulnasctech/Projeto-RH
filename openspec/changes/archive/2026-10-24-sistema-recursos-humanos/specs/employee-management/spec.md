# Spec Delta

## Purpose

Definir o comportamento para consultar e manter os cadastros de funcionários do RH, com informações persistidas no Xano e acesso restrito a usuários autorizados.

## ADDED Requirements

### Requirement: Consulta de funcionários
O sistema MUST apresentar funcionários persistidos no backend e MUST permitir localizar registros por pesquisa e filtros disponíveis. A interface MUST distinguir carregamento, resultado vazio e falha de consulta.

#### Scenario: Consulta concluída com funcionários
- **WHEN** um usuário autorizado abre a lista de funcionários e o backend retorna registros
- **THEN** o sistema apresenta os dados retornados pelo backend

#### Scenario: Consulta sem resultados
- **WHEN** uma consulta válida não encontra funcionários
- **THEN** o sistema apresenta um estado vazio e não exibe dados demonstrativos como se fossem registros reais

#### Scenario: Falha ao consultar funcionários
- **WHEN** o backend não conclui a consulta
- **THEN** o sistema informa a falha sem substituir o resultado por uma lista fictícia

### Requirement: Manutenção de funcionários
O sistema MUST permitir a usuários com perfil RH criar e editar funcionários com os dados aceitos pelo backend, incluindo departamento, cargo, data de admissão e estado. O sistema MUST validar os dados antes do envio e apresentar os erros de validação ou de persistência.

#### Scenario: Cadastro de funcionário válido
- **WHEN** um usuário RH envia um cadastro válido
- **THEN** o backend persiste o funcionário e o sistema confirma o sucesso

#### Scenario: Edição de funcionário
- **WHEN** um usuário RH altera dados válidos de um funcionário existente
- **THEN** o backend persiste as alterações e a interface apresenta os dados atualizados

#### Scenario: Cadastro ou edição rejeitados
- **WHEN** os dados enviados são inválidos ou o backend rejeita a operação
- **THEN** o sistema informa o problema e preserva os valores necessários para correção

### Requirement: Desativação de funcionário
O sistema MUST permitir que um usuário com perfil RH desative um funcionário sem remover o registro histórico, usando o estado inativo aceito pelo backend.

#### Scenario: Desativação confirmada
- **WHEN** um usuário RH confirma a desativação de um funcionário
- **THEN** o backend marca o funcionário como inativo e o registro continua consultável

#### Scenario: Desativação não autorizada
- **WHEN** um usuário sem perfil RH tenta desativar um funcionário
- **THEN** o backend rejeita a operação e o estado do funcionário não muda
