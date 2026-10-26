# Tasks

## 1. Contrato e autorização no Xano

- [x] 1.1 Criar consulta protegida de opções do formulário usando os schemas reais de usuários e departamentos; verificar com testes que só Gestor RH acessa e que a resposta contém apenas ID, nome, e-mail de exibição e departamento.
- [x] 1.2 Restringir o POST de funcionários aos campos permitidos, validar usuário/departamento existentes e não associados, definir situação inicial como “Ativo” e rejeitar salário ou campos de conta; testar autorização e ausência de gravação parcial.

## 2. Serviços de cadastro

- [x] 2.1 Implementar no serviço Python a consulta autenticada de opções e o envio do cadastro usando a URL configurada e o token da sessão; testar respostas válidas, erros HTTP, acesso negado e falha de conexão.

## 3. Formulário Reflex

- [x] 3.1 Implementar no estado Reflex o carregamento das opções, validação dos campos e envio do cadastro; testar campos obrigatórios, tratamento de erros e preservação dos valores.
- [x] 3.2 Conectar “Novo colaborador” ao formulário com estados de carregamento, erro e sucesso; após sucesso, recarregar a lista e verificar que nenhum dado fictício ou salário é exibido.

## 4. Verificação integrada

- [x] 4.1 Executar testes focados de serviço, estado/interface e contrato Xano; verificar criação autorizada, rejeição sem perfil Gestor RH e atualização da listagem após sucesso.
- [x] 4.2 Executar `reflex compile --dry` e `openspec validate cadastrar-funcionario --strict`; corrigir erros antes de concluir a change.
