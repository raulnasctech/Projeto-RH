# Proposal

## Why

O sistema já permite definir jornadas semanais, mas ainda não registra as marcações realizadas nem oferece ao Gestor RH uma visão diária de quem iniciou, concluiu ou deixou o ponto incompleto. Esta mudança conecta as jornadas à assiduidade e oferece ao colaborador um único fluxo para registrar as próprias marcações.

## What Changes

- Registrar marcações diárias vinculadas ao colaborador autenticado e à data de trabalho, seguindo a jornada cadastrada.
- Oferecer ao colaborador uma tela única que libera as marcações na ordem esperada: entrada e saída final sem intervalo; entrada, saída para intervalo, retorno e saída final quando houver intervalo.
- Oferecer ao Gestor RH um painel diário com estados de aguardando horário, não iniciou, ponto aberto, incompleto, concluído, folga e jornada não cadastrada.
- Autorizar marcações somente para o colaborador vinculado à identidade autenticada; autorizar o painel diário somente para Gestor RH.
- Validar no backend identidade, vínculo, jornada aplicável, sequência e horário das marcações, sem confiar em identificadores ou estado enviados pela interface.
- Tratar batidas ausentes após o horário esperado como incompletas e ausência de entrada após o início previsto como não iniciou; antes do início, exibir aguardando horário.
- Não incluir funcionários inativos na lista operacional diária; exibir funcionários ativos sem jornada como jornada não cadastrada, sem classificá-los como falta.

Fora do escopo: ajustes manuais de batidas, aprovação de correções, banco de horas, cálculo de horas extras, folha de pagamento, geolocalização, biometria, notificações e relatórios históricos.

## Capabilities

### New Capabilities

- `attendance-management`: registro seguro de ponto pelo colaborador e acompanhamento diário de presença pelo Gestor RH com base na jornada cadastrada.

### Modified Capabilities

Nenhuma. A autorização e o vínculo específicos de ponto serão definidos nesta nova capacidade, sem alterar os contratos existentes de gestão de funcionários ou jornadas.

## Impact

- Interface Reflex e estado de sessão: identificar o perfil autenticado e apresentar a tela de ponto ao colaborador ou o painel diário ao Gestor RH.
- Serviços Python: integrar com consulta do estado diário e registro da próxima batida, validando as respostas do Xano.
- Xano: persistência de marcações, endpoints de colaborador e Gestor RH, validação de sequência e resolução segura do colaborador associado ao usuário autenticado.
- Testes: cobrir transições das batidas, estados do painel, vínculo de identidade, autorização e falhas das APIs.
