# Tasks

## 1. Contrato da API de funcionários

- [x] 1.1 Ajustar `GET /employees` para retornar nome do usuário e nome do departamento relacionados, além dos campos de listagem acordados; verificar o contrato com um teste que confirme a estrutura e a ausência de salário.
- [x] 1.2 Preservar autenticação e autorização `Gestor RH` ao alterar a consulta; executar os testes de contrato de autorização e confirmar que chamadas sem permissão continuam rejeitadas.

## 2. Serviço de consulta

- [x] 2.1 Criar serviço de leitura de funcionários que envie o token da sessão ao endpoint protegido e valide a resposta; testar registros válidos e campos relacionados ausentes.
- [x] 2.2 Tratar resposta vazia, erro HTTP e falha de conexão sem converter erro em lista vazia; executar testes unitários para cada resultado.

## 3. Interface Reflex

- [x] 3.1 Conectar o estado da página à consulta ao abrir a tela e remover os colaboradores fixos; verificar que a lista preenchida contém somente registros devolvidos pela API.
- [x] 3.2 Implementar apresentação de carregamento, lista vazia e erro, incluindo valores opcionais como “Não informado”; verificar cada estado com testes ou validação observável da interface.
- [x] 3.3 Manter o tratamento de sessão rejeitada e de acesso negado coerente com a autenticação e a autorização existentes; testar a resposta para sessão expirada e usuário sem perfil autorizado.
- [x] 3.4 Evitar consultas de identidade redundantes após login e antes da listagem, mantendo a verificação em caso de resposta negada; testar a contagem de chamadas e o tratamento de sessão expirada.

## 4. Verificação integrada

- [x] 4.1 Executar os testes focados de serviço, estado/interface e contrato da API; confirmar que todos passam e que dados demonstrativos e salário não aparecem na lista.
- [x] 4.2 Executar a compilação/verificação Reflex e validar manualmente a lista com conta autorizada e acesso negado; verificar o estado vazio com o teste de resposta vazia.
- [x] 4.3 Executar `openspec validate listar-colaboradores-reais --strict` e corrigir eventuais erros antes de concluir a change.
