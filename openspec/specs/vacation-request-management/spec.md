# vacation-request-management Specification

## Purpose

Permitir ao Gestor RH registrar e administrar solicitações de férias com dados persistidos no Xano, decisões controladas e um indicador confiável de colaboradores em férias.

## Requirements

### Requirement: Tabela de solicitações de férias no Xano
O Xano MUST disponibilizar uma tabela `vacation_requests` para persistir solicitações de férias. A tabela MUST conter identificador e data de criação, referência obrigatória a um registro de `employees`, datas obrigatórias de início e fim, situação e referência opcional ao usuário de `user` que decidiu a solicitação. A situação inicial MUST ser `Pendente`; os únicos valores permitidos MUST ser `Pendente`, `Aprovada` e `Rejeitada`. A criação ou adequação da tabela MUST preservar registros existentes quando a tabela já existir.

#### Scenario: Tabela ainda não existe
- **WHEN** a mudança é aplicada a um workspace Xano sem a tabela `vacation_requests`
- **THEN** a tabela é criada com os campos e relacionamentos definidos e pode armazenar solicitações ligadas a funcionários e usuários existentes

#### Scenario: Tabela já existe com registros
- **WHEN** a mudança é aplicada a um workspace Xano onde `vacation_requests` já existe e contém registros
- **THEN** a estrutura é adequada sem apagar esses registros e os relacionamentos apontam para `employees` e `user`

### Requirement: Endpoints de férias protegidos por perfil RH
A API de solicitações de férias MUST exigir token válido. O usuário com perfil exatamente igual a `Gestor RH` MUST poder consultar todas as solicitações, criar solicitações em nome de funcionários existentes e decidir solicitações pendentes. Um funcionário autenticado MUST poder criar e consultar somente solicitações vinculadas ao seu próprio cadastro. A decisão de solicitações MUST continuar exclusiva ao Gestor RH. A validação de perfil e de vínculo MUST ocorrer no backend antes de ler ou alterar solicitações, independentemente do cliente que chama a API.

#### Scenario: Chamada sem autenticação válida
- **WHEN** um cliente consulta, cria ou tenta decidir uma solicitação sem token válido
- **THEN** a API rejeita a chamada sem retornar ou alterar dados de férias

#### Scenario: Usuário autenticado sem perfil Gestor RH
- **WHEN** um usuário autenticado cujo perfil não é exatamente `Gestor RH` chama um endpoint administrativo de férias
- **THEN** a API rejeita a chamada sem retornar ou alterar dados de férias, salvo as operações próprias permitidas ao funcionário

#### Scenario: Usuário Gestor RH autenticado
- **WHEN** o token válido identifica um usuário com `role` igual a `Gestor RH`
- **THEN** a API permite a operação administrativa solicitada, sujeita às validações da solicitação e da transição de situação

#### Scenario: Funcionário autenticado consulta ou cria solicitação própria
- **WHEN** o token válido identifica um funcionário vinculado a exatamente um cadastro ativo
- **THEN** a API permite criar uma solicitação vinculada a esse cadastro e consultar somente solicitações desse funcionário

#### Scenario: Funcionário tenta acessar dados alheios ou decidir solicitação
- **WHEN** um funcionário tenta consultar solicitações de outro cadastro ou aprovar/rejeitar uma solicitação
- **THEN** a API rejeita a operação sem revelar dados alheios nem alterar a solicitação

### Requirement: Solicitação e acompanhamento de férias pelo funcionário
O sistema MUST permitir que um funcionário autenticado com vínculo ativo solicite férias informando início e fim, sem poder escolher outro funcionário como titular. O backend MUST iniciar a solicitação como `Pendente` e associá-la ao cadastro vinculado à identidade autenticada. O funcionário MUST poder consultar seu próprio histórico e acompanhar o status decidido pelo Gestor RH. A interface MUST distinguir carregamento, lista vazia e falha de consulta.

#### Scenario: Funcionário envia período válido
- **WHEN** um funcionário vinculado informa um período com datas válidas e início não posterior ao fim e confirma a solicitação
- **THEN** o backend cria a solicitação como `Pendente` para o cadastro vinculado ao token autenticado e a interface confirma o envio

#### Scenario: Funcionário sem vínculo ativo ou período inválido
- **WHEN** a conta não está vinculada a exatamente um funcionário ativo ou o início é posterior ao fim
- **THEN** o backend rejeita a criação sem criar solicitação e a interface informa a falha

#### Scenario: Funcionário consulta seu histórico
- **WHEN** o funcionário abre sua área de férias e a API retorna solicitações
- **THEN** a interface exibe somente os períodos e status associados ao cadastro vinculado ao usuário autenticado

#### Scenario: Funcionário ainda não tem solicitações
- **WHEN** a API retorna uma lista válida sem solicitações próprias
- **THEN** a interface apresenta um estado vazio distinto dos estados de carregamento e erro

#### Scenario: Gestor RH decide uma solicitação do funcionário
- **WHEN** o Gestor RH aprova ou rejeita uma solicitação pendente criada pelo funcionário
- **THEN** a decisão confirmada aparece no histórico do funcionário como `Aprovada` ou `Rejeitada` e não pode ser decidida novamente

#### Scenario: Falha ao consultar o histórico do funcionário
- **WHEN** a API rejeita a consulta ou fica indisponível
- **THEN** a interface apresenta uma mensagem de erro e não apresenta registros fictícios nem uma lista vazia como resultado da falha

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
