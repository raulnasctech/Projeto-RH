# Design

## Context

Ver [proposal.md](./proposal.md) para motivação e [specs/employee-management/spec.md](./specs/employee-management/spec.md) para o contrato observável. A página Reflex já lista funcionários através de um serviço Python e tem um botão “Novo colaborador” sem ação. O POST de funcionários exige autenticação e chama a autorização Gestor RH, mas recebe um `dblink` amplo. As consultas locais genéricas de usuários e departamentos não aplicam essa autorização e usam os nomes `users` e `departments`, diferentes dos schemas locais `user` e `departaments`.

## Goals / Non-Goals

**Goals:**

- Criar um fluxo de cadastro pequeno, testável e coerente com a sessão Reflex existente.
- Usar somente vínculos existentes e dados mínimos para os seletores.
- Garantir que o Xano valide perfil, referências e campos gravados.

**Non-Goals:**

- Criar contas, redefinir credenciais ou enviar convites.
- Implementar edição, desativação, cadastro de departamentos ou indicadores.
- Alterar o modelo de autenticação ou introduzir dependências de frontend.

## Decisions

1. **Associar uma conta existente e um departamento existente.** O formulário seleciona uma conta ainda não associada a funcionário e um departamento cadastrado. Isso evita criar identidade de autenticação nesta etapa e reduz associações duplicadas. Criar contas ou aceitar IDs digitados livremente foram descartados.

2. **Fornecer opções por uma consulta administrativa protegida e mínima.** Não reutilizar diretamente as consultas genéricas atuais de usuários e departamentos: elas não verificam o perfil RH e seus nomes de tabela divergem dos schemas locais. A consulta do formulário usa os schemas locais `user` e `departaments`, valida Gestor RH e retorna somente IDs e nomes de exibição; para usuários, inclui e-mail apenas para distinguir opções. Senha, CPF, celular e salário não são retornados.

3. **Restringir o contrato de criação a uma lista permitida de campos.** Manter a autenticação e a autorização Gestor RH já presentes no POST, substituindo a entrada ampla por campos explícitos. Validar usuário e departamento no backend, impedir vínculo duplicado, aceitar cargo e data de admissão opcionais, definir situação inicial como “Ativo” e não aceitar salário ou dados de conta no payload.

4. **Manter chamadas externas nos serviços Python e a sessão no servidor.** O serviço de cadastro e opções segue o padrão HTTP existente, usa a URL de RH configurada e o token mantido no estado servidor. O estado Reflex controla carregamento, erro e sucesso; após sucesso, atualiza a lista através do serviço existente. A alternativa de chamar o Xano diretamente do navegador foi descartada para não expor o token.

5. **Usar um formulário na página de colaboradores.** A ação “Novo colaborador” abre o formulário com seletores carregados do backend. Falhas de opções ou persistência permanecem explícitas e não são convertidas em opções ou registros fictícios.

## Risks / Trade-offs

- **Os contratos locais de usuários/departamentos podem não refletir o workspace Xano ativo.** → Confirmar nomes de tabelas, campos e autorização do branch ativo antes de publicar; manter testes do contrato versionado.
- **Uma falha após o envio pode deixar dúvida sobre a persistência.** → Só apresentar sucesso depois de resposta válida do backend e recarregar a lista; em falha, preservar os valores para nova tentativa.
- **As opções de usuário podem mudar entre consulta e gravação.** → Revalidar no POST a existência e a disponibilidade dos vínculos; não confiar apenas nos seletores da interface.

