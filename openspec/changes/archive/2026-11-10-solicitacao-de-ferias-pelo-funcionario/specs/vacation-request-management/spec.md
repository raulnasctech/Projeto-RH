# Spec Delta

## MODIFIED Requirements

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

## ADDED Requirements

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
