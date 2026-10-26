# Design

## Context

Ver `proposal.md` para a motivação. O cadastro e a listagem já usam Reflex no cliente e endpoints protegidos no Xano. A tabela aceita registros antigos relacionados a uma conta; o endpoint de leitura já utiliza o nome funcional quando existe e mantém o nome da conta como fallback legado.

## Goals / Non-Goals

**Goals:**
- Registrar o nome funcional diretamente no colaborador e manter o vínculo com uma conta opcional para compatibilidade com registros existentes.
- Atualizar a experiência da listagem após confirmação do backend sem ocultar registros durante uma atualização.
- Manter autorização e validação de cadastro no backend.

**Non-Goals:**
- Criar contas, credenciais ou permissões de acesso para os colaboradores cadastrados.
- Alterar o modelo de autenticação ou incluir salário no formulário.

## Decisions

- **Nome funcional no registro de funcionário:** enviar `name` e departamento no cadastro, sem exigir `user_id`. Manter `user_id` opcional e usar o nome da conta como fallback na leitura de registros legados. Isso evita a criação artificial de contas e preserva os dados existentes; substituir integralmente o vínculo de conta quebraria compatibilidade.
- **Opções de departamento em endpoint próprio:** obter somente departamentos por uma rota estática separada (`/employee-form-options`). A rota anterior `/employees/form-options` conflita com a rota dinâmica `/employees/{employees_id}` no Xano, portanto o caminho separado evita interpretação do texto como identificador.
- **Atualização da interface depois da resposta bem-sucedida:** incluir o novo colaborador na lista somente após confirmação do backend, evitando mostrar um cadastro que falhou. Durante atualizações, manter os registros já exibidos; substituir a lista apenas quando uma resposta válida chegar.
- **Validação e autorização no Xano:** exigir perfil Gestor RH e validar nome e departamento no servidor, sem confiar apenas nas validações da interface.

## Risks / Trade-offs

- [Registros legados podem não ter `name`] → manter o fallback ao nome da conta relacionada e não exigir migração destrutiva.
- [A interface pode mostrar detalhes locais ligeiramente diferentes da resposta normalizada da API] → construir o item a partir dos campos confirmados no formulário e da resposta de criação, e atualizar os dados em uma consulta posterior normal.
- [Uma configuração Xano desatualizada pode não expor o endpoint ou o novo campo] → publicar a alteração de schema e rotas antes de disponibilizar a interface correspondente.

## Migration Plan

1. Publicar o campo funcional opcional `name` e os endpoints de leitura/criação compatíveis no Xano.
2. Publicar a rota protegida `/employee-form-options` e verificar acesso de Gestor RH.
3. Disponibilizar o cliente Reflex com o formulário nominal e atualização da listagem.
4. Em caso de rollback do cliente, os dados novos permanecem no campo `name`; não remover o campo nem alterar registros legados. Uma reversão do endpoint deve manter a leitura com fallback ao nome da conta.
