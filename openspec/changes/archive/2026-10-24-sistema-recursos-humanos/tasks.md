# Tasks

## 1. Contratos e autorização no Xano

- [ ] 1.1 Inventariar endpoints e schemas de autenticação, funcionários e departamentos e registrar contratos de entrada/saída verificados nos arquivos Xano.
- [ ] 1.2 Confirmar como o backend identifica o perfil RH e proteger os endpoints administrativos; verificar com testes que chamadas sem sessão ou sem perfil RH são rejeitadas.
- [ ] 1.3 Confirmar operações disponíveis para pesquisa, filtros, paginação e desativação; validar cada contrato com chamadas de teste ao Xano.

## 2. Integração compartilhada com o Xano

- [ ] 2.1 Implementar cliente HTTP compartilhado com URL configurável, timeout e erros normalizados; testar respostas de sucesso, erro HTTP e falha de conexão.
- [ ] 2.2 Configurar as variáveis de ambiente e atualizar `.env.example` e `.gitignore`; verificar que nenhum valor secreto está rastreado pelo Git.
- [ ] 2.3 Implementar serviços Python para autenticação, funcionários e departamentos usando o cliente compartilhado; validar contratos com testes simulados.

## 3. Autenticação e controle de acesso

- [ ] 3.1 Adaptar o login ao contrato confirmado no Xano e manter token e identidade em sessão no servidor, sem expor token ao navegador; testar login válido e inválido.
- [ ] 3.2 Proteger páginas e ações administrativas conforme o perfil devolvido pelo backend; testar acesso permitido e negado.
- [ ] 3.3 Implementar logout e tratamento de sessão expirada ou rejeitada; testar encerramento da sessão e redirecionamento para autenticação.

## 4. Gestão de funcionários

- [ ] 4.1 Implementar consulta de funcionários com pesquisa e filtros suportados pela API; testar resultados, consulta vazia e erro.
- [ ] 4.2 Implementar cadastro e edição com validação e associação a departamento e cargo; testar persistência e rejeição de dados inválidos.
- [ ] 4.3 Implementar desativação pelo estado do funcionário, preservando o registro histórico; testar a mudança de estado e a rejeição de usuário sem permissão.
- [ ] 4.4 Conectar a tela de funcionários aos serviços e apresentar estados de carregamento, vazio, sucesso e erro; verificar que nenhum dado demonstrativo aparece como dado real.

## 5. Gestão de departamentos

- [ ] 5.1 Implementar consulta, cadastro e edição de departamentos com autorização do backend; testar persistência, listagem e erros de validação.
- [ ] 5.2 Integrar departamentos e cargo aos formulários de funcionários; testar associação válida e rejeição de departamento inválido ou indisponível.

## 6. Painel de RH

- [ ] 6.1 Substituir indicadores fixos por totais de funcionários ativos, admissões no mês e distribuição por departamento; comparar os valores com as respostas do backend.
- [ ] 6.2 Implementar carregamento, estado sem dados e falha de consulta nos indicadores; verificar que falhas nunca são apresentadas como resultados válidos.

## 7. Verificação integrada

- [ ] 7.1 Adicionar ou atualizar testes automatizados para serviços, validações, autorização e fluxos de interface; executar a suíte e confirmar aprovação.
- [ ] 7.2 Verificar isolamento de sessão, ausência de tokens e dados pessoais em logs e proteção de chamadas diretas ao Xano; registrar o resultado dos testes.
- [ ] 7.3 Executar a verificação/compilação Reflex e validar os fluxos de login, funcionários, departamentos e painel em ambiente de desenvolvimento.
- [ ] 7.4 Executar `openspec validate sistema-recursos-humanos --strict` e corrigir qualquer erro de validação antes de concluir a mudança.
