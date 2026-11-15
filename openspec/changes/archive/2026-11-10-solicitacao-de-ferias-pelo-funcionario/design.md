# Design

## Context

A capability existente já persiste solicitações em `vacation_requests`, mantém os status `Pendente`, `Aprovada` e `Rejeitada`, e oferece ao Gestor RH consulta geral, cadastro em nome de um funcionário e decisão de pedidos pendentes. O vínculo entre usuário e funcionário é representado por `employees.user_id`; a API de ponto do funcionário já identifica o cadastro pela identidade autenticada e exige um único vínculo ativo. Consulte `proposal.md` e a delta spec para motivação e contrato comportamental.

## Goals / Non-Goals

**Goals:**
- Isolar as operações do funcionário no backend usando o usuário autenticado como fonte do vínculo.
- Preservar os contratos atuais de gestão do RH e o esquema existente da tabela.
- Disponibilizar ao funcionário uma tela de pedido e acompanhamento sem afetar a tela administrativa.

**Non-Goals:**
- Alterar a estrutura da tabela ou os estados existentes.
- Permitir edição ou cancelamento pelo funcionário.
- Introduzir regras de saldo, conflitos entre períodos, datas passadas ou notificações.

## Decisions

- **Adicionar endpoints próprios para o funcionário e manter os endpoints atuais do RH.** Criar operações de consulta e criação em `/my_vacation_requests`. O caminho estático distinto evita colisão com a rota existente `/vacation_requests/{vacation_requests_id}`, cujo parâmetro numérico pode interpretar `me` como ID inválido. Isso evita ampliar a autorização de endpoints administrativos existentes e preserva seus GUIDs e comportamento.
- **Derivar o funcionário exclusivamente de `$auth.id`.** No backend, localizar o vínculo em `employees.user_id`, exigir exatamente um cadastro ativo, e usar esse ID na consulta/criação. A operação do funcionário não deve aceitar `employees_id` como titular fornecido pelo cliente. Uma conta sem vínculo único ativo é rejeitada.
- **Manter a decisão no fluxo existente do RH.** O endpoint de decisão continua autorizado somente ao Gestor RH e só altera solicitações pendentes. Após a decisão, a consulta própria retorna o status persistido, sem sincronização adicional ou armazenamento duplicado no cliente.
- **Usar a mesma página de férias com conteúdo e carregamento condicionados ao perfil.** O Gestor RH mantém formulário administrativo, indicador e fila com ações de decisão; o funcionário recebe formulário próprio e histórico sem ações administrativas. Incluir a navegação de férias na área do funcionário e encaminhar o carregamento da rota para o fluxo correspondente ao perfil.
- **Reutilizar os serviços HTTP e corrigir a autenticação Bearer antes de conectá-los ao novo fluxo.** O helper de autorização do serviço existente atualmente não interpola o token na forma `Bearer <token>`. Corrigir esse envio e cobrir o cabeçalho em teste, em vez de criar um segundo mecanismo HTTP.
- **Não alterar a tabela nem restringir datas além da ordem válida.** A tabela já guarda funcionário, período, status e usuário decisor. Sem regra de negócio adicional definida, manter o critério já usado: datas válidas e início não posterior ao fim; pedidos em períodos passados ou sobrepostos não serão bloqueados por esta mudança.

## Risks / Trade-offs

- [Um endpoint próprio pode ser configurado com autorização incorreta no Xano] → Validar perfil, vínculo e titularidade no servidor; adicionar testes de contrato cobrindo isolamento, acesso negado e ausência de `employees_id` controlável pelo cliente.
- [A tela de férias pode acionar o carregamento administrativo para funcionários] → Separar o carregamento por perfil no handler da rota e testar ambos os perfis, inclusive redirecionamentos e estados de erro.
- [A correção do cabeçalho Bearer altera o serviço comum de férias] → Cobrir autenticação e erros HTTP nos testes de serviço, preservando as chamadas e respostas atuais do RH.

## Migration Plan

1. Adicionar os endpoints próprios de consulta e criação no Xano, mantendo os endpoints administrativos e os dados atuais.
2. Atualizar serviços e estados Reflex, então habilitar a tela e navegação de férias para funcionários.
3. Validar contratos, autorização, isolamento de dados e build/compilação da aplicação.
4. Não é necessária migração de dados. Em caso de rollback, desabilitar os novos endpoints e a entrada da interface do funcionário; manter os endpoints e registros existentes do RH.
