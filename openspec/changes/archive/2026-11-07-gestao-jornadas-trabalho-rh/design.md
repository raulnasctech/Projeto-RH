# Design

## Context

Ver `proposal.md` para motivação e `specs/work-schedule-management/spec.md` para o contrato comportamental. O app usa Reflex, integra com o Xano por serviços Python e os endpoints RH já validam o perfil Gestor RH com a função de autorização existente. Não há tabela, serviço ou tela de jornadas no estado atual. A tabela `employees` tem identificador próprio e vínculo opcional com `user`; a listagem de colaboradores resolve o nome a partir da conta relacionada quando necessário.

## Goals / Non-Goals

**Goals:**

- Fazer do backend Xano a fonte de verdade da jornada recorrente por colaborador.
- Permitir horários diferentes em cada dia da semana, mantendo uma jornada única por colaborador.
- Garantir validação e persistência de uma semana completa sem atualizações parciais.
- Reutilizar os padrões atuais de autenticação, apresentação de estados e testes.

**Non-Goals:**

- Criar batidas de ponto, cálculo de atraso, horas extras ou fechamento de folha.
- Manter versões históricas ou jornadas com data futura de início.
- Suportar mais de um turno ou intervalo por dia, escalas noturnas atravessando a meia-noite, feriados ou banco de horas.

## Decisions

1. **Uma configuração JSON por colaborador.** Armazenar uma linha em `work_schedules` por colaborador, com `employees_id` único e um campo JSON `weekly_schedule` contendo exatamente os sete dias. Cada dia guarda se é trabalhado e, quando aplicável, os minutos desde meia-noite de entrada, saída e intervalo. A branch live `v1` não contém estrutura nem dados de jornada; portanto, não há migração de dados existentes.

2. **Semana como unidade atômica.** A interface envia a configuração semanal completa. Os endpoints validam todos os dias e horários e persistem o JSON em uma única operação de banco (`add` ou `patch`), evitando que uma falha deixe apenas parte da semana atualizada. Um índice único em `employees_id` impede jornadas duplicadas por colaborador. A alternativa de múltiplas linhas por dia foi rejeitada porque exigiria atomicidade transacional entre várias gravações.

3. **Intervalo opcional e único.** Em dia de trabalho, entrada e saída são obrigatórias e o intervalo pode estar ausente. Se presente, os dois limites são obrigatórios e devem ficar estritamente entre entrada e saída. Dia de folga não contém horários. Os horários são normalizados para minutos inteiros desde meia-noite, facilitando validação e comparação no Xano. Esta decisão atende a uma jornada diária convencional; múltiplos intervalos e turnos noturnos ficam para uma mudança futura.

4. **API de RH protegida.** Novos endpoints de consulta e gravação usam autenticação `user` e a função `RH API/authorize employee manager` antes de acessar tabelas, no mesmo padrão da API de colaboradores. A autorização não depende de verificações na interface.

5. **Serviço e interface Reflex.** Um serviço Python integra com a API de jornada, valida respostas e mantém erros explícitos. A tela seleciona um colaborador, mostra os sete dias, permite editar e distinguir estados de carregamento, não cadastrado, salvo e falha. A tela não trata os valores locais do formulário como persistidos até a confirmação do backend.

6. **Testes por contrato e comportamento.** Cobrir estrutura da tabela e endpoints, autorização, validações temporais e atomicidade, parsing do serviço e estados da interface. Executar os testes focados e a compilação Reflex.

## Risks / Trade-offs

- [Alterações concorrentes podem substituir a mesma semana] → Gravar a semana em uma única operação e assegurar unicidade por colaborador com índice no backend.
- [O modelo atual não guarda vigência nem histórico] → Tratar a jornada como recorrente e atual; mudanças históricas ou futuras exigem evolução explícita do contrato.
- [Jornadas com turno atravessando a meia-noite não cabem na ordenação dentro de um mesmo dia] → Rejeitá-las nesta versão e mantê-las fora do escopo.
- [Um colaborador pode não ter uma conta relacionada] → Associar a jornada pelo `employees.id`; usar o nome funcional ou o nome relacionado disponível apenas para exibição.

## Migration Plan

1. Inspecionar o workspace e branch Xano escolhidos para confirmar ausência ou presença de dados de jornadas antes da alteração; preservar dados existentes.
2. Criar ou adequar a tabela e publicar os endpoints protegidos e transacionais; confirmar o contrato e as referências no Xano.
3. Implementar o serviço e a interface Reflex usando somente os endpoints publicados.
4. Validar com testes automatizados e revisão manual do fluxo de consulta, cadastro e edição como Gestor RH; não inserir registros de teste em produção sem autorização.
5. Em rollback, reverter interface e endpoints sem apagar registros de jornadas persistidos.
