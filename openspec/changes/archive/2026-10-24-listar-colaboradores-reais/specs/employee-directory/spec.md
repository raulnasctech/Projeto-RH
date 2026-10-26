# Spec Delta

## Purpose

Permitir que o perfil de RH consulte na aplicação os colaboradores realmente cadastrados, identificados por seus nomes e departamentos relacionados, sem apresentar dados fictícios como se fossem registros do sistema.

## ADDED Requirements

### Requirement: Listagem real de colaboradores com dados relacionados
O sistema MUST consultar a API autorizada de funcionários e apresentar os registros retornados pelo backend. Cada registro apresentado MUST identificar o colaborador pelo nome relacionado ao usuário e informar o departamento relacionado, além de cargo, admissão e situação quando esses campos estiverem disponíveis. A resposta da listagem MUST incluir somente os campos necessários à tela e MUST NOT expor salário. Quando uma relação ou campo opcional não estiver disponível, a interface MUST apresentar “Não informado”, sem substituir o valor por um identificador ou dado demonstrativo.

#### Scenario: RH consulta colaboradores cadastrados
- **WHEN** um usuário autorizado abre a listagem e a API retorna funcionários
- **THEN** a interface apresenta os registros retornados com nome e departamento relacionados e os demais campos disponíveis, sem incluir salário

#### Scenario: Relação ou campo opcional indisponível
- **WHEN** um registro retornado não possui usuário, departamento ou outro campo opcional disponível
- **THEN** a interface apresenta “Não informado” para o valor ausente e não exibe o identificador da relação como se fosse um nome

### Requirement: Estados de carregamento, lista vazia e falha
Enquanto a consulta estiver em andamento, o sistema MUST indicar que a lista está carregando. Quando a consulta terminar sem registros, MUST apresentar um estado vazio. Quando a consulta falhar ou for negada, MUST apresentar um estado de erro apropriado e MUST NOT apresentar dados fictícios nem tratar a falha como uma lista vazia.

#### Scenario: Consulta em andamento
- **WHEN** a tela inicia a consulta de colaboradores
- **THEN** a interface informa que os dados estão sendo carregados

#### Scenario: Nenhum colaborador cadastrado
- **WHEN** a API retorna uma lista válida sem registros
- **THEN** a interface apresenta uma mensagem de lista vazia, distinta do estado de carregamento e do estado de erro

#### Scenario: API indisponível ou consulta rejeitada
- **WHEN** a API retorna erro, a conexão falha ou o usuário não tem autorização
- **THEN** a interface apresenta uma mensagem de erro apropriada e não apresenta registros demonstrativos nem uma lista vazia como resultado da falha
