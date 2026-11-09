# Tasks

## 1. Dados e API no Xano

- [x] 1.1 Inspecionar no workspace e branch Xano escolhidos se já existem tabelas ou jornadas; registrar dados existentes e definir a migração sem perda, validando o resultado por pull do schema. (Workspace 151047, branch live `v1`: o pull de metadados não encontrou tabela nem endpoint de jornada, portanto não há dados de jornada a migrar.)
- [x] 1.2 Criar a tabela `work_schedules` com uma linha por colaborador, vínculo único e semana JSON com os sete dias, status trabalhado/folga e horários; verificar o schema por pull e confirmar que os dados existentes foram preservados. (Publicada na branch `v1`; o pull confirmou o relacionamento `employees_id` e o índice único. Nenhum registro foi importado.)
- [x] 1.3 Implementar endpoints autenticados de consulta e gravação da semana, chamando autorização Gestor RH antes do acesso a dados; validar colaborador, presença dos sete dias e ordem dos horários e persistir a semana em uma única operação, cobrindo chamadas permitidas, negadas e payloads inválidos em testes de contrato. (Implementação local e testes de contrato concluídos.)
- [x] 1.4 Publicar primeiro a estrutura e depois os endpoints no workspace autorizado, sempre após preview; confirmar por pull os objetos e referências publicados sem criar registros de teste de produção. (Tabela publicada e conferida por pull; funções e endpoints publicados após preview e conferidos em novo pull. Nenhum registro de produção foi criado.)

## 2. Integração e interface Reflex

- [x] 2.1 Implementar serviço Python para consultar e salvar jornadas semanais com o token de sessão, validação estrita do payload e erros explícitos; cobrir respostas válidas, erros HTTP, acesso negado e horários inválidos com testes unitários.
- [x] 2.2 Implementar estado Reflex para localizar colaborador, carregar a jornada e salvar os sete dias, distinguindo carregamento, jornada inexistente, sucesso e falha; verificar esses estados em testes de estado.
- [x] 2.3 Criar a página Reflex de gestão de jornadas, com edição de dias trabalhados/folgas e horários; verificar submissão válida, exibição de dados confirmados e preservação do último estado salvo após falha.

## 3. Validação integrada

- [x] 3.1 Executar testes focados de schema, autorização, validação de períodos, atomicidade, serviço e interface; corrigir falhas e confirmar a suíte focada aprovada. (Suíte completa: 119 testes aprovados.)
- [x] 3.2 Executar `reflex compile --dry` e `openspec validate gestao-jornadas-trabalho-rh --strict`; confirmar compilação e validade dos artefatos OpenSpec.
