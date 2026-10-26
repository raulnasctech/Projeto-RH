# Tasks

## 1. Autorização reutilizável no Xano

- [x] 1.1 Implementar verificação backend que carrega o registro `user` indicado pelo token autenticado e compara `role` exatamente com `Gestor RH`; validar role correta e diferente com chamadas reais, além de validar estaticamente o comportamento de role ausente.

## 2. Proteção dos endpoints de funcionários

- [x] 2.1 Confirmar em `GET /employees` que a conta autenticada com `role` `Gestor RH` recebe acesso e que uma conta sem esse perfil é negada.
- [x] 2.2 Exigir autenticação e chamar a verificação de perfil antes de qualquer leitura ou escrita nos endpoints GET/POST `employees` e GET/PATCH/DELETE `employees/{employees_id}`; confirmar que os cinco endpoints retornam HTTP 401 sem token.
- [x] 2.3 Confirmar que `GET /employees/{employees_id}` permite consulta para a conta `Gestor RH` e nega a conta sem esse perfil, usando um registro existente sem alterá-lo.
- [x] 2.4 Confirmado pelo usuário que os testes de POST/PATCH/DELETE funcionaram para os perfis e cenários previstos.
- [x] 2.5 Confirmado pelo usuário que os testes de respostas autorizadas e chamadas negadas funcionaram sem problemas relatados.

## 3. Validação e implantação

- [x] 3.1 Confirmado pelo usuário que a tabela `user` possui o campo `role` com valor exatamente igual a `Gestor RH` para a conta RH, sem registrar dados pessoais.
- [x] 3.2 Executar testes relevantes (23 passaram), `openspec validate proteger-api-funcionarios --strict` e confirmar pelo usuário que os testes dos cinco endpoints funcionaram.
