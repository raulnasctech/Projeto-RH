# Tasks

## 1. Autorização e API Xano

- [x] 1.1 Criar endpoints de consulta e criação de férias próprias que identifiquem o funcionário pelo usuário autenticado, exijam exatamente um vínculo ativo e rejeitem titular informado pelo cliente; verificar com testes de contrato Xano para vínculo válido, ausência/duplicidade de vínculo e isolamento.
- [x] 1.2 Manter os endpoints administrativos de listagem, criação em nome de funcionário e decisão exclusivos ao Gestor RH; verificar que os GUIDs e testes de contrato existentes continuam válidos e que funcionários não conseguem decidir.
- [x] 1.3 Preservar status inicial `Pendente` e validação de datas nos novos endpoints; verificar rejeição de período inválido e persistência da solicitação vinculada ao funcionário autenticado.

## 2. Serviço de férias

- [x] 2.1 Implementar chamadas de serviço para consulta e criação próprias, sem enviar identificador de funcionário pelo cliente, e tratar erros HTTP/autorização sem converter falhas em lista vazia; verificar com testes unitários de serviço.
- [x] 2.2 Validar o envio do cabeçalho `Authorization` no formato Bearer e a rejeição de token ausente; verificar por teste unitário do serviço e preservar as chamadas e respostas existentes do RH.

## 3. Estado e interfaces Reflex

- [x] 3.1 Implementar estado de carregamento, envio, lista vazia, sucesso e erro para as solicitações próprias do funcionário; verificar com testes de estado cobrindo resposta pendente, consulta sem registros e falhas.
- [x] 3.2 Adaptar a rota e navegação de férias para exibir formulário e histórico próprios ao funcionário, sem controles de decisão ou dados de outros colaboradores; verificar com testes de estado/UI e acesso de rota.
- [x] 3.3 Preservar a tela administrativa do Gestor RH e confirmar que pedidos feitos por funcionários aparecem na fila com ações apenas enquanto pendentes; verificar com testes de estado existentes e novos cenários de integração.

## 4. Validação integrada

- [x] 4.1 Executar os testes de férias e contratos Xano (`test_vacation_service.py`, `test_vacation_state.py` e `test_xano_vacation_contract.py`) e corrigir regressões relacionadas à mudança.
- [x] 4.2 Validar a change com `openspec validate solicitacao-de-ferias-pelo-funcionario --strict` e compilar a aplicação Reflex; registrar e resolver qualquer falha causada pelos artefatos ou implementação.
