# Tasks

## 1. Dados e API no Xano

- [x] 1.1 Consultar no workspace e branch Xano escolhidos se `vacation_requests` existe e contém registros; registrar o estado antes de qualquer alteração e verificar a conclusão pela comparação posterior do schema e dos dados existentes. Confirmado: tabela ausente na branch `v1` live; portanto, não há registros dessa tabela a preservar.
- [x] 1.2 Criar ou adequar `xano/table/vacation_requests.xs` com relação obrigatória a `employees`, datas, situações permitidas e relação opcional `decided_by` com `user`; verificar o schema exportado e confirmar que registros anteriores foram preservados. O preview Xano confirma a criação do schema; não há tabela remota anterior.
- [x] 1.3 Proteger os endpoints de consulta, cadastro e decisão para aceitar somente token válido de usuário `Gestor RH`; verificar os contratos de API com chamadas anônimas, usuário não RH e usuário RH. O pull remoto confirma autenticação e autorização por perfil em todos os endpoints; os cinco endpoints retornaram HTTP 401 sem token.
- [x] 1.4 Implementar no Xano cadastro como `Pendente`, validação de funcionário e período e decisão condicional somente de registros pendentes, atribuindo `decided_by` do token autenticado; verificar casos de sucesso, registro inexistente, data inválida e decisão repetida. Regras conferidas nos scripts publicados e cobertas pelos testes de contrato/serviço; não foi criada solicitação de teste na produção.
- [x] 1.5 Publicar primeiro a tabela e depois os endpoints no workspace autorizado, sem apagar a tabela existente; confirmar no Xano os relacionamentos, os endpoints ativos e os resultados dos testes de autorização e fluxo. Tabela e cinco endpoints publicados; pull confirmou os relacionamentos e a API rejeitou chamadas anônimas. O fluxo autenticado de gravação não foi executado em produção para evitar inserir dados de teste.

## 2. Integração e interface Reflex

- [x] 2.1 Criar ou estender o serviço Python de solicitações de férias para listar, cadastrar e decidir com token, validação de resposta e erros explícitos; verificar os testes unitários do serviço para respostas válidas e falhas do Xano.
- [x] 2.2 Criar a área Reflex de gestão de férias com seleção de funcionário, cadastro de período, listagem de estados e ações para solicitações pendentes; verificar cadastro confirmado, lista vazia e mensagens de erro sem dados demonstrativos.
- [x] 2.3 Atualizar o indicador do painel para contar funcionários distintos com férias aprovadas vigentes; verificar casos de períodos válidos, futuros, encerrados, não aprovados e solicitações múltiplas do mesmo funcionário.

## 3. Validação integrada

- [x] 3.1 Executar os testes focados de férias e autorização e corrigir falhas; confirmar que os testes cobrem criação de tabela/contrato, controle de perfil, validações e estados da interface.
- [x] 3.2 Executar `reflex compile --dry` e validar a change com `openspec validate gestao-solicitacoes-ferias-rh --strict`; confirmar que a aplicação compila e que os requisitos e cenários OpenSpec passam na validação.
