# work-schedule-management Specification

## Purpose

Permitir ao Gestor RH definir uma jornada semanal recorrente por colaborador, com horários próprios para cada dia, para apoiar a organização do trabalho e servir como referência a futuras funcionalidades de assiduidade.

## Requirements

### Requirement: Gestão de jornada semanal protegida
O sistema MUST permitir que usuários autenticados com perfil Gestor RH consultem, criem e atualizem a jornada semanal dos colaboradores. O backend MUST validar o perfil antes de acessar ou alterar jornadas e MUST rejeitar usuários sem esse perfil. Cada colaborador MUST possuir no máximo uma jornada semanal recorrente.

#### Scenario: Gestor RH consulta jornadas
- **WHEN** um usuário autenticado com perfil Gestor RH consulta as jornadas
- **THEN** o backend retorna as jornadas persistidas associadas aos colaboradores correspondentes

#### Scenario: Usuário sem perfil Gestor RH consulta ou altera jornadas
- **WHEN** um usuário sem token válido ou sem perfil Gestor RH tenta consultar, criar ou atualizar uma jornada
- **THEN** o backend rejeita a chamada sem retornar ou alterar dados de jornada

#### Scenario: Jornada inexistente para um colaborador
- **WHEN** o Gestor RH consulta a jornada de um colaborador que ainda não possui uma
- **THEN** o sistema informa que não há jornada cadastrada, sem criar dados implicitamente

### Requirement: Jornada recorrente configurável por dia da semana
O Gestor RH MUST poder configurar, para cada dia da semana, se o colaborador trabalha ou folga. Cada dia trabalhado MUST ter horários de entrada e saída; o intervalo é opcional, mas, quando informado, MUST conter início e fim. O backend MUST exigir exatamente uma configuração para cada um dos sete dias e rejeitar colaborador inexistente e horários incompletos ou fora de ordem sem salvar dados parciais. O sistema MUST manter no máximo uma jornada semanal por colaborador.

#### Scenario: Cadastro ou atualização válida da jornada
- **WHEN** o Gestor RH envia uma configuração válida para os dias da semana de um colaborador existente
- **THEN** o backend persiste a jornada recorrente e a consulta subsequente retorna a configuração confirmada

#### Scenario: Dia de folga
- **WHEN** um dia é configurado como folga
- **THEN** a jornada desse dia não exige horários de entrada, saída ou intervalo

#### Scenario: Dia trabalhado sem intervalo
- **WHEN** um dia trabalhado possui horários de entrada e saída válidos e nenhum intervalo
- **THEN** o backend aceita e persiste a jornada desse dia

#### Scenario: Intervalo informado
- **WHEN** um dia trabalhado inclui intervalo
- **THEN** o backend exige os dois horários do intervalo e valida a ordem entrada, início do intervalo, fim do intervalo e saída

#### Scenario: Dados da jornada inválidos
- **WHEN** o Gestor RH envia horários incompletos, horários em ordem inválida, dias ausentes ou um colaborador inexistente
- **THEN** o backend rejeita toda a alteração e mantém a jornada anteriormente persistida sem mudanças parciais

### Requirement: Interface de gestão de jornadas
O sistema MUST apresentar ao Gestor RH uma área para localizar colaboradores e consultar, cadastrar ou editar suas jornadas por dia da semana. A interface MUST distinguir carregamento, ausência de jornada e falha de consulta ou gravação, MUST exibir confirmação após persistência e MUST apresentar erros de validação sem descartar a jornada anteriormente salva.

#### Scenario: Carregamento e consulta da jornada
- **WHEN** o Gestor RH abre a área de jornadas e seleciona um colaborador
- **THEN** a interface indica o carregamento e apresenta a jornada persistida ou um estado explícito de jornada não cadastrada

#### Scenario: Salvamento confirmado
- **WHEN** o backend confirma o cadastro ou atualização da jornada
- **THEN** a interface apresenta confirmação e os horários persistidos para cada dia

#### Scenario: Falha de consulta ou salvamento
- **WHEN** a API rejeita ou não consegue concluir a operação
- **THEN** a interface informa a falha e não apresenta dados não confirmados como se estivessem salvos
