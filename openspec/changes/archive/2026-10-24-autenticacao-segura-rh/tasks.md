# Tasks

## 1. Contratos de autenticação

- [x] 1.1 Confirmar nos arquivos/contratos do Xano os formatos de sucesso e erro de `/auth/login`, `/auth/signup` e `/auth/me`; registrar fixtures usados pelos testes.

## 2. Sessão segura e páginas internas

- [x] 2.1 Mover o token para estado backend-only por sessão, deixar de ler `LocalStorage` para autenticação e remover as chaves legadas; verificar que o token não aparece no estado enviado ao navegador.
- [x] 2.2 Só concluir login ou cadastro depois que `/auth/me` confirmar uma identidade válida; testar credenciais inválidas, respostas incompletas e falhas de conexão sem criar sessão.
- [x] 2.3 Exigir sessão nas páginas internas e redirecionar acessos diretos sem autenticação; testar acesso permitido e negado para todas as rotas internas registradas.

## 3. Logout e sessão expirada

- [x] 3.1 Fazer logout limpar token e identidade da sessão antes do redirecionamento; testar que a sessão não pode ser reutilizada depois de sair.
- [x] 3.2 Tratar respostas do Xano que indiquem token expirado ou rejeitado, limpar a sessão e pedir nova autenticação; cobrir o fluxo com teste simulado.

## 4. Verificação integrada

- [x] 4.1 Adicionar testes automatizados para login, cadastro existente, isolamento entre sessões, proteção das rotas, logout e expiração; confirmar que token e credenciais não aparecem em logs ou dados enviados ao cliente.
- [x] 4.2 Executar os testes focados e a verificação/compilação Reflex disponível no projeto; validar manualmente login, acesso direto a rota interna e logout.
