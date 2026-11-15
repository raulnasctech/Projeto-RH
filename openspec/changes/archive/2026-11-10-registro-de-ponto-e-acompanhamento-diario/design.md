# Design

## Context

Ver `proposal.md` para motivação e `specs/attendance-management/spec.md` para os comportamentos exigidos. O app usa Reflex, mantém o token de autenticação no estado do servidor e integra com o Xano por serviços Python. O endpoint existente `/auth/me` já retorna `role`, mas o serviço Python descarta esse campo e o estado atual não separa as interfaces por perfil. A API de RH já possui autorização de Gestor RH e a tabela `work_schedules` armazena uma semana recorrente por colaborador, sem histórico de versões. O vínculo `employees.user_id` é opcional.

Não há configuração de fuso horário encontrada no app ou nos contratos consultados. Esta change considera `America/Sao_Paulo` como fuso de operação do sistema para derivar data, dia da semana e horários previstos; instantes registrados continuam sendo horários do relógio do servidor, convertidos para esse fuso na apresentação.

## Goals / Non-Goals

**Goals:**

- Usar o servidor Xano como autoridade para identidade, vínculo, sequência de batidas, relógio e estados do painel.
- Preservar a jornada efetivamente usada no dia após a primeira batida, mesmo que o Gestor RH edite a jornada durante o expediente.
- Evitar que chamadas repetidas ou concorrentes criem registros duplicados ou avancem duas etapas.
- Reutilizar os serviços Python, o estado Reflex e as convenções de APIs protegidas já existentes.

**Non-Goals:**

- Permitir edição ou exclusão de batidas, correção administrativa, auditoria de alterações, histórico de jornadas, processamento de folha ou sincronização com sistemas externos.
- Criar uma conta de funcionário automaticamente ou reparar vínculos de conta ausentes/duplicados.

## Decisions

1. **Perfil como parte da identidade autenticada.** Estender o objeto de usuário autenticado e o estado Reflex para conservar o `role` retornado pelo `/auth/me`. Após o login, direcionar `Gestor RH` para o acompanhamento e usuários vinculados a um colaborador ativo para a tela de ponto. A decisão de exibir uma rota não substitui a autorização nos endpoints; perfis ausentes, desconhecidos ou sem vínculo único recebem um estado de acesso negado. Isso evita tratar qualquer usuário autenticado como RH, como a interface atual estática poderia sugerir.

2. **Resolver o colaborador exclusivamente pelo token.** Endpoints de colaborador consultam `employees` pelo identificador do usuário autenticado e exigem exatamente um vínculo ativo. Não recebem `employees_id` do cliente. Endpoints do painel reutilizam a função de autorização existente para exigir `role == "Gestor RH"` e retornam apenas nome, departamento/cargo se necessário, estado e horários de ponto.

3. **Eventos imutáveis por tipo de batida.** Criar uma tabela `attendance_punches` com colaborador, `work_date`, tipo da batida, `created_at` do servidor e uma cópia da jornada diária no evento de entrada. Um índice único composto por colaborador, data e tipo de batida impede duplicidade mesmo sob concorrência. A sequência é derivada no backend dos eventos persistidos; o cliente não envia tipo de batida, horário, data ou identificador de colaborador. A cópia da jornada na primeira batida fixa a expectativa daquele dia, sem introduzir histórico geral de jornadas.

4. **Transição calculada no servidor.** Para cada chamada, o Xano resolve o próximo tipo de evento pela lista já persistida, valida a hora atual contra a hora prevista e adiciona apenas esse evento. Uma colisão no índice único resulta em rejeição explícita; o cliente recarrega o estado confirmado. O horário previsto controla quando a ação fica liberada, mas não substitui o instante real gravado. Batidas atrasadas continuam válidas e são classificadas pelo horário previsto, não corrigidas para a hora planejada.

5. **Status derivado para o dia atual.** A consulta do painel une colaboradores ativos, jornada aplicável e eventos do dia corrente em `America/Sao_Paulo`. Antes da entrada prevista, uma jornada sem batida fica `Aguardando horário`; desde a entrada prevista fica `Não iniciou`. Com batida inicial, fica `Ponto aberto` enquanto a próxima batida ainda não venceu, `Incompleto` quando ela venceu e `Concluído` após a última batida. Folga e ausência de jornada são estados próprios, não faltas. Essa decisão mantém um painel operacional sem criar tabela de resumos que possa divergir dos eventos.

6. **Rotas Reflex separadas por função.** A tela do colaborador é única e apresenta jornada, marcações confirmadas e somente a próxima ação aplicável. O painel RH é uma rota diária separada, com filtros visuais por estado e estados explícitos de carregamento, vazio e erro. Após cada registro, a tela do colaborador atualiza-se a partir da resposta confirmada pelo Xano.

7. **Validação por contrato e transições.** Criar testes unitários para jornada e estados calculados, testes do serviço Python para respostas válidas/inválidas e autorização, testes de contrato dos arquivos Xano para proteção/índices, e testes do estado Reflex para redirecionamento, próxima ação e resultados de falha. A validação de concorrência deve confirmar a rejeição de duplicidade no índice único do backend.

## Risks / Trade-offs

- [O vínculo opcional ou duplicado de conta deixa o funcionário sem tela de ponto] → Rejeitar o acesso com mensagem explícita; corrigir o cadastro permanece operação de RH fora desta change.
- [O Xano pode retornar timestamps em UTC enquanto o dia de operação é local] → Derivar data e estado com o fuso `America/Sao_Paulo` no backend e testar mudanças de dia perto da meia-noite.
- [A cópia diária da jornada não oferece histórico geral] → Guardá-la somente no evento de entrada para fixar a sequência do dia; alterações planejadas para datas futuras continuam fora do escopo.
- [Falhas de rede após uma gravação confirmada podem deixar a tela desatualizada] → Consultar novamente os eventos do dia antes de habilitar uma nova ação e não sinalizar confirmação com base apenas no estado local.
- [O índice composto pode exigir adequação se já houver tabela de batidas criada manualmente] → Inspecionar o workspace Xano antes da migração, preservar dados e resolver duplicidades antes de criar a restrição.

## Migration Plan

1. Inspecionar branch e workspace Xano de destino para confirmar se já existe tabela ou endpoint de ponto; preservar quaisquer dados existentes.
2. Criar/adequar a tabela de eventos e índice único composto, publicar endpoints autenticados de consulta e registro do próprio ponto e endpoint RH do acompanhamento diário.
3. Atualizar serviços e estado de autenticação Reflex para conservar perfil e direcionar as rotas; implementar tela única do colaborador e painel diário do RH.
4. Validar autorização, sequências sem/com intervalo, estados antes/depois dos horários previstos, vínculo ausente/ambíguo, consultas e colisões concorrentes em ambiente de teste.
5. Em rollback, remover ou desativar rotas e endpoints sem apagar eventos persistidos; manter as jornadas existentes intactas.
