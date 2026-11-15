# attendance-management Specification

## Purpose

Permitir que cada colaborador registre as próprias batidas de ponto de acordo com sua jornada semanal e que o Gestor RH acompanhe a situação diária da equipe. A identidade e as regras de transição devem ser verificadas pelo backend para manter os registros confiáveis.

## Requirements

### Requirement: Identificação e autorização para acesso ao ponto
O sistema MUST identificar o perfil do usuário autenticado. O backend MUST permitir o painel diário somente a usuários cujo perfil seja exatamente `Gestor RH`. Para registrar ou consultar o próprio ponto, MUST resolver a identidade autenticada para exatamente um colaborador ativo; o identificador do colaborador MUST ser obtido no backend e MUST NOT ser escolhido pelo cliente. Usuários sem perfil autorizado, sem vínculo único ou com vínculo a colaborador inativo MUST ter a operação rejeitada sem expor ou alterar registros de terceiros.

#### Scenario: Gestor RH abre o acompanhamento diário
- **WHEN** um usuário autenticado com perfil `Gestor RH` consulta o painel diário
- **THEN** o backend retorna os dados operacionais do dia sem permitir que o cliente substitua a data ou acesse dados fora do escopo autorizado

#### Scenario: Colaborador consulta e registra o próprio ponto
- **WHEN** um usuário autenticado está vinculado a exatamente um colaborador ativo e acessa a área de ponto
- **THEN** o sistema apresenta somente a jornada e as marcações desse colaborador e permite registrar a próxima batida aplicável

#### Scenario: Perfil ou vínculo não autorizado
- **WHEN** um usuário sem o perfil exigido, sem vínculo a colaborador ativo ou com vínculo ambíguo tenta acessar o ponto
- **THEN** o backend rejeita a chamada sem retornar dados pessoais ou criar marcações

### Requirement: Registro sequencial de batidas conforme a jornada
O sistema MUST disponibilizar ao colaborador uma única tela para consultar a próxima ação esperada e registrar suas próprias batidas. O backend MUST usar a jornada recorrente válida para a data e MUST aceitar somente a próxima batida da sequência: entrada e saída final em dia trabalhado sem intervalo; entrada, saída para intervalo, retorno do intervalo e saída final em dia com intervalo. A sequência MUST respeitar o horário da batida anterior, registrar o horário oficial no backend e impedir registros duplicados ou fora de ordem. Uma batida MUST NOT ser aceita em dia de folga ou sem jornada cadastrada. Batidas atrasadas podem ser registradas na ordem correta e MUST manter o horário efetivamente registrado.

#### Scenario: Colaborador inicia o ponto
- **WHEN** o colaborador vinculado registra a entrada em um dia de trabalho com jornada cadastrada
- **THEN** o backend registra o horário da entrada e apresenta a próxima batida prevista para aquele dia

#### Scenario: Jornada sem intervalo
- **WHEN** o colaborador registra a entrada em uma jornada sem intervalo e depois registra a saída final
- **THEN** o backend aceita exatamente essas duas batidas em ordem e conclui o registro diário

#### Scenario: Jornada com intervalo
- **WHEN** o colaborador registra entrada, saída para intervalo, retorno e saída final, nessa ordem
- **THEN** o backend registra cada horário e conclui o registro diário somente após a saída final

#### Scenario: Batida antecipada, duplicada ou fora de ordem
- **WHEN** o colaborador tenta registrar uma batida antes do horário esperado, repetir uma batida já registrada ou pular uma etapa
- **THEN** o backend rejeita a operação e mantém as marcações persistidas inalteradas

#### Scenario: Batida atrasada na ordem correta
- **WHEN** o horário previsto para uma batida já passou, mas o colaborador ainda não a registrou
- **THEN** o backend permite registrar essa próxima batida na ordem correta com o horário atual do servidor, sem alterar horários anteriores

#### Scenario: Folga ou jornada ausente
- **WHEN** o colaborador tenta registrar ponto em dia de folga ou sem jornada cadastrada para aquele dia
- **THEN** o backend rejeita a operação sem criar registro diário

### Requirement: Acompanhamento diário de ponto pelo Gestor RH
O painel do Gestor RH MUST apresentar os colaboradores ativos e a situação do ponto na data operacional atual, com estados distintos para `Aguardando horário`, `Não iniciou`, `Ponto aberto`, `Incompleto`, `Concluído`, `Folga` e `Jornada não cadastrada`. Colaboradores ativos sem jornada MUST aparecer como `Jornada não cadastrada` e não podem ser contabilizados como faltosos. Antes do horário previsto para entrada, um dia trabalhado sem batida MUST aparecer como `Aguardando horário`; a partir do início previsto, sem entrada, MUST aparecer como `Não iniciou`. Um registro iniciado MUST aparecer como `Ponto aberto` enquanto a próxima batida ainda não venceu e como `Incompleto` quando uma batida esperada estiver vencida. Um registro MUST aparecer como `Concluído` após todas as batidas exigidas pela jornada. A interface MUST distinguir carregamento, resultado vazio e falha da consulta, sem apresentar dados fictícios ou transformar falha em lista vazia.

#### Scenario: Painel antes do início da jornada
- **WHEN** o Gestor RH consulta o dia antes do início previsto de um colaborador que ainda não registrou entrada
- **THEN** o colaborador aparece como `Aguardando horário`, e não como faltoso

#### Scenario: Colaborador não iniciou após o início previsto
- **WHEN** o horário previsto de entrada já chegou e não existe batida de entrada
- **THEN** o painel apresenta `Não iniciou` para o colaborador

#### Scenario: Ponto iniciado e próxima batida ainda não vencida
- **WHEN** há uma entrada válida e a próxima batida ainda não chegou ao seu horário previsto
- **THEN** o painel apresenta `Ponto aberto` e indica a próxima ação esperada

#### Scenario: Batida esperada vencida ou jornada concluída
- **WHEN** uma batida esperada não foi registrada até seu horário previsto, ou todas as batidas da jornada foram registradas
- **THEN** o painel apresenta respectivamente `Incompleto` ou `Concluído`, com os horários efetivamente registrados

#### Scenario: Folga e jornada não cadastrada
- **WHEN** a jornada do colaborador indica folga ou não existe uma jornada cadastrada
- **THEN** o painel apresenta respectivamente `Folga` ou `Jornada não cadastrada`, sem classificar a pessoa como faltosa

#### Scenario: Consulta do painel em andamento, vazia ou com falha
- **WHEN** o painel está carregando, não existem colaboradores ativos ou a API falha
- **THEN** a interface apresenta estados distintos de carregamento, lista vazia e erro e não apresenta dados não confirmados

### Requirement: Integridade e proteção dos registros de ponto
A API MUST exigir autenticação válida para consultar ou registrar marcações. O backend MUST determinar o colaborador, a data operacional e os horários a partir da sessão e do relógio do servidor, aplicar a sequência de forma atômica e impedir que chamadas concorrentes criem batidas duplicadas ou avancem duas etapas. O painel MUST retornar somente os dados funcionais necessários, sem salário, credenciais ou tokens. Falhas e rejeições MUST ser informadas sem apresentar a operação como concluída.

#### Scenario: Chamada sem sessão válida
- **WHEN** um cliente sem token válido tenta consultar ou registrar marcações
- **THEN** a API rejeita a chamada sem expor dados ou persistir alterações

#### Scenario: Chamadas concorrentes para a mesma etapa
- **WHEN** duas solicitações tentam registrar simultaneamente a próxima batida do mesmo colaborador
- **THEN** somente uma transição é persistida e a outra recebe uma rejeição explícita sem criar duplicidade

#### Scenario: Falha de consulta ou gravação
- **WHEN** o backend não consegue concluir a consulta ou persistência de uma batida
- **THEN** a interface informa a falha e não mostra a marcação como confirmada
