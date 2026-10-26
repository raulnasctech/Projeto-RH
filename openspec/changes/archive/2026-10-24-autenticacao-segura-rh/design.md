# Design

## Context

Consulte [proposal.md](./proposal.md) para a motivação e [specs/authentication/spec.md](./specs/authentication/spec.md) para o comportamento esperado. Atualmente, `State.auth_token` e `State.user_name` usam `rx.LocalStorage`; login e cadastro compartilham a rotina `_authenticate`, que consulta `/auth/me`. As páginas internas são registradas individualmente e ainda não têm uma verificação comum de sessão.

## Goals / Non-Goals

**Goals:**

- Reaproveitar os endpoints Xano existentes de login, cadastro e consulta da identidade.
- Isolar o token no estado server-side individual do Reflex e evitar sincronizá-lo com o cliente.
- Centralizar a decisão de concluir a autenticação na confirmação do Xano e da identidade.
- Aplicar a verificação de sessão às páginas internas sem alterar os fluxos de cadastro ou o visual das telas.

**Non-Goals:**

- Autorizar operações de RH no Xano ou alterar permissões de endpoints de funcionários e departamentos.
- Criar um provedor de identidade novo ou alterar os contratos do Xano.
- Implementar serviços compartilhados para domínios fora da autenticação.

## Decisions

1. **Manter o Xano como autoridade de autenticação e identidade.** O sistema só cria a sessão depois de confirmar a autenticação e a consulta de identidade. Não confiar em nome ou perfil fornecido pelo navegador. A alternativa de tratar qualquer resposta de login bem-sucedida como sessão válida foi rejeitada porque a rotina atual não falha quando `/auth/me` não confirma a identidade.

2. **Armazenar o token em variável backend-only do Reflex.** A documentação do Reflex distingue variáveis sincronizadas com o cliente das variáveis backend-only, identificadas por `_`. O token ficará nesse estado privado por sessão; somente os dados de apresentação estritamente necessários, como o nome, poderão ser sincronizados. `LocalStorage` e cookies acessíveis ao cliente foram rejeitados para o token.

3. **Verificar a sessão no servidor nas páginas internas.** A verificação será vinculada ao carregamento das páginas registradas como internas, evitando depender de links ou redirecionamentos do navegador. A tela de acesso e o cadastro continuam públicos. Esse controle protege o acesso à interface, mas não substitui a autorização de cada endpoint no Xano, que fica fora desta change.

4. **Tratar rejeição do Xano como encerramento da sessão.** As chamadas autenticadas deverão usar uma rotina que reconhece respostas de sessão inválida, limpa os dados locais e encaminha o usuário para autenticação. Não manter uma sessão parcialmente válida quando `/auth/me` falhar.

## Risks / Trade-offs

- **O contrato real de `/auth/me` pode diferir do formato atualmente presumido.** → Confirmar as respostas de login, cadastro e identidade no Xano antes de adaptar a sessão; cobrir campos ausentes e erros nos testes.
- **O Reflex sincroniza variáveis comuns com o navegador.** → Manter o token em variável backend-only e verificar nos testes que ele não aparece no estado/deltas enviados ao cliente.
- **Chaves `LocalStorage` de versões anteriores podem permanecer nos navegadores.** → Ignorar esses valores na nova versão e remover as chaves legadas na migração; confirmar no navegador que o token antigo não é reutilizado.
- **Uma guarda de página não protege endpoints de dados por si só.** → Não tratar esta change como autorização de backend; proteger operações do Xano em uma change própria antes de conectar cadastros reais.

## Migration Plan

1. Confirmar os contratos dos endpoints existentes e o comportamento que identifica token expirado ou rejeitado.
2. Implementar a sessão server-side e a verificação de acesso, mantendo o login e cadastro atuais.
3. Remover e deixar de consumir os valores legados do armazenamento do navegador.
4. Testar login, cadastro, navegação direta, logout, expiração, isolamento entre usuários e ausência do token no cliente.
5. Em caso de falha, reverter a alteração da aplicação; não alterar dados ou endpoints do Xano nesta change.
