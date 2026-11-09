# Spec Delta

## Purpose

Permitir ao Gestor RH registrar e administrar solicitações de férias com dados persistidos no Xano, decisões controladas e um indicador confiável de colaboradores em férias.

## ADDED Requirements

### Requirement: Tabela de solicitações de férias no Xano
O Xano MUST disponibilizar uma tabela `vacation_requests` para persistir solicitações de férias. A tabela MUST conter identificador e data de criação, referência obrigatória a um registro de `employees`, datas obrigatórias de início e fim, situação e referência opcional ao usuário de `user` que decidiu a solicitação. A situação inicial MUST ser `Pendente`; os únicos valores permitidos MUST ser `Pendente`, `Aprovada` e `Rejeitada`. A criação ou adequação da tabela MUST preservar registros existentes quando a tabela já existir.

#### Scenario: Tabela ainda não existe
- **WHEN** a mudança é aplicada a um workspace Xano sem a tabela `vacation_requests`
- **THEN** a tabela é criada com os campos e relacionamentos definidos e pode armazenar solicitações ligadas a funcionários e usuários existentes

#### Scenario: Tabela já existe com registros
- **WHEN** a mudança é aplicada a um workspace Xano onde `vacation_requests` já existe e contém registros
- **THEN** a estrutura é adequada sem apagar esses registros e os relacionamentos apontam para `employees` e `user`

### Requirement: Endpoints de férias protegidos por perfil RH
A API de solicitações de férias MUST exigir token válido e MUST permitir consulta, criação e decisão somente quando o usuário autenticado em `user` tiver `role` exatamente igual a `Gestor RH`. A validação MUST ocorrer no backend antes de ler ou alterar solicitações, independentemente do cliente que chama a API.

#### Scenario: Chamada sem autenticação válida
- **WHEN** um cliente consulta, cria ou tenta decidir uma solicitação sem token válido
- **THEN** a API rejeita a chamada sem retornar ou alterar dados de férias

#### Scenario: Usuário autenticado sem perfil Gestor RH
- **WHEN** um usuário autenticado cujo perfil não é exatamente `Gestor RH` chama um endpoint de férias
- **THEN** a API rejeita a chamada sem retornar ou alterar dados de férias

#### Scenario: Usuário Gestor RH autenticado
- **WHEN** o token válido identifica um usuário com `role` igual a `Gestor RH`
- **THEN** a API permite a operação solicitada, sujeita às validações da solicitação e da transição de situação

### Requirement: Cadastro e consulta de solicitações pelo RH
O sistema MUST permitir que o Gestor RH registre uma solicitação em nome de um funcionário existente, informando datas de início e fim válidas, e MUST iniciar a solicitação com situação `Pendente`. A área de gestão MUST listar as solicitações persistidas com funcionário, período e situação. A interface MUST apresentar estados distintos de carregamento, lista vazia e falha, sem exibir dados fictícios ou apresentar falha como lista vazia.

#### Scenario: Cadastro válido em nome de funcionário
- **WHEN** o Gestor RH seleciona um funcionário existente, informa datas válidas em que o início não é posterior ao fim e confirma o cadastro
- **THEN** o backend persiste a solicitação como `Pendente` e a interface apresenta o registro confirmado

#### Scenario: Funcionário inexistente ou período inválido
- **WHEN** o cadastro referencia funcionário inexistente ou informa data de início posterior à data de fim
- **THEN** o backend rejeita o cadastro sem criar registro parcial e a interface informa o erro

#### Scenario: Consulta sem solicitações
- **WHEN** a API retorna uma lista válida sem solicitações
- **THEN** a interface apresenta um estado vazio distinto dos estados de carregamento e erro

#### Scenario: Falha ao consultar solicitações
- **WHEN** a API rejeita a consulta ou fica indisponível
- **THEN** a interface apresenta uma mensagem de erro e não apresenta registros fictícios nem uma lista vazia como resultado da falha

### Requirement: Aprovação e rejeição de solicitações pendentes
O sistema MUST permitir que o Gestor RH aprove ou rejeite somente solicitações com situação `Pendente`. A API MUST rejeitar decisões para solicitações inexistentes ou já decididas e MUST persistir a nova situação e o identificador do usuário Gestor RH que tomou a decisão. Uma decisão confirmada MUST refletir-se na lista sem permitir uma segunda decisão sobre a mesma solicitação.

#### Scenario: Aprovação de solicitação pendente
- **WHEN** o Gestor RH aprova uma solicitação existente com situação `Pendente`
- **THEN** a API persiste a situação `Aprovada` e o usuário responsável pela decisão e a interface atualiza o registro

#### Scenario: Rejeição de solicitação pendente
- **WHEN** o Gestor RH rejeita uma solicitação existente com situação `Pendente`
- **THEN** a API persiste a situação `Rejeitada` e o usuário responsável pela decisão e a interface atualiza o registro

#### Scenario: Decisão repetida ou solicitação inexistente
- **WHEN** o Gestor RH tenta aprovar ou rejeitar uma solicitação já decidida ou inexistente
- **THEN** a API rejeita a operação e mantém os dados persistidos sem alteração

### Requirement: Indicador de colaboradores atualmente em férias
O indicador de férias do painel MUST contar cada funcionário uma única vez quando houver ao menos uma solicitação `Aprovada` para esse funcionário cujo período inclui a data atual. Solicitações pendentes, rejeitadas ou aprovadas fora do período atual MUST NOT ser contadas.

#### Scenario: Funcionário com férias aprovadas em andamento
- **WHEN** um funcionário possui solicitação aprovada cuja data de início é anterior ou igual à data atual e cuja data de fim é posterior ou igual à data atual
- **THEN** o indicador conta esse funcionário uma vez

#### Scenario: Solicitação não vigente ou duplicada
- **WHEN** solicitações de um funcionário estão pendentes, rejeitadas, fora do período atual ou há mais de uma solicitação aprovada vigente
- **THEN** solicitações não vigentes não aumentam o indicador e o funcionário é contado no máximo uma vez
