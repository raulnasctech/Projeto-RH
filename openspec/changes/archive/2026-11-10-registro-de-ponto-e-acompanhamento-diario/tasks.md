# Tasks

> As definições Xano foram publicadas no workspace `Raul's Workspace`, branch `v1`. O pull de verificação confirmou os cinco documentos, e os três endpoints responderam HTTP 401 sem autenticação (não 404).

## 1. Persistência e APIs Xano

- [x] 1.1 Inspecionar o workspace/branch Xano de destino e verificar se já existem tabela, endpoints ou registros de ponto; registrar como o contrato será adequado sem apagar dados.
- [x] 1.2 Criar ou adequar a tabela de eventos de ponto com jornada diária copiada na primeira entrada e índice único composto por colaborador, data e tipo; verificar o schema e a restrição de duplicidade.
- [x] 1.3 Implementar endpoints autenticados para consultar e registrar o ponto do usuário vinculado, resolvendo um único colaborador ativo pelo token e validando jornada, próxima batida, horário de servidor e concorrência; verificar autorização e transições por testes de contrato.
- [x] 1.4 Implementar endpoint do painel diário protegido pelo perfil `Gestor RH`, derivando estados para colaboradores ativos com jornadas, folgas e jornadas ausentes no fuso `America/Sao_Paulo`; verificar estados e campos retornados sem dados sensíveis.
- [x] 1.5 Cobrir os contratos Xano com testes de autenticação, vínculo ausente/ambíguo, sequência, batidas atrasadas, índice único e dados retornados pelo painel; executar a suíte focada de contratos.

## 2. Integração Python e sessão

- [x] 2.1 Preservar o perfil `role` retornado por `/auth/me` no usuário autenticado e no estado Reflex, incluindo limpeza da sessão; verificar testes de autenticação e que o token continue apenas no servidor.
- [x] 2.2 Criar serviços Python para consulta/registro do ponto do colaborador e consulta diária RH, validando identificadores, estados, horários e erros das APIs; verificar testes unitários de respostas válidas e inválidas.
- [x] 2.3 Implementar no estado Reflex o carregamento por perfil, a próxima ação, a atualização após batida confirmada e os estados de erro sem confirmação local; verificar testes do estado para cada fluxo.

## 3. Interfaces e validação integrada

- [x] 3.1 Criar a tela única de ponto do colaborador com jornada, batidas confirmadas e apenas a próxima ação liberada; verificar fluxo com e sem intervalo e estado de acesso negado.
- [x] 3.2 Criar o painel diário do Gestor RH com lista operacional, estados e horários e mensagens distintas de carregamento, vazio e falha; verificar cada estado e a ausência de registros fictícios.
- [x] 3.3 Executar testes direcionados e compilação Reflex, corrigindo falhas relacionadas à mudança; confirmar redirecionamento por perfil, autorização de backend e integração das duas telas.
