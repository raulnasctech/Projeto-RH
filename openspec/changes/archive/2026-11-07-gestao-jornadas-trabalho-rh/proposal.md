# Proposal

## Why

O sistema ainda não possui uma fonte persistida para a jornada semanal dos colaboradores, embora o painel já se refira à gestão da jornada. Sem horários e dias de trabalho definidos por colaborador, futuras consultas de assiduidade não terão uma referência confiável para comparar os registros de ponto.

## What Changes

- Permitir ao Gestor RH consultar, cadastrar e editar a jornada semanal de cada colaborador.
- Configurar cada dia da semana independentemente, com indicação de dia trabalhado ou folga, horários de entrada e saída e intervalo opcional.
- Validar os horários no backend, rejeitando períodos incompletos ou inválidos sem salvar dados parciais.
- Restringir consultas e alterações a usuários autenticados com perfil Gestor RH.
- Manter uma jornada semanal recorrente por colaborador; histórico, vigência futura, múltiplos turnos no mesmo dia e marcação de ponto ficam fora desta mudança.

## Capabilities

### New Capabilities

- `work-schedule-management`: gestão protegida de jornadas semanais recorrentes configuráveis por dia para os colaboradores.

### Modified Capabilities

Nenhuma.

## Impact

- Interface Reflex: nova área para consultar e manter a jornada semanal dos colaboradores, com estados de carregamento, vazio e erro.
- Serviços e testes Python: integração autenticada com os endpoints de jornadas e validações de resposta e períodos.
- Xano: nova estrutura persistente e endpoints para consultar, criar e atualizar jornadas, protegidos pela autorização Gestor RH existente.
- Não serão alterados os fluxos de autenticação, cadastro de colaboradores, férias nem APIs de marcação de ponto.
