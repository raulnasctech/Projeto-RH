# Proposal

## Why

O projeto já possui uma interface inicial em Reflex e endpoints no Xano para autenticação, funcionários e departamentos, mas as telas de RH ainda apresentam dados demonstrativos e os fluxos não formam uma experiência administrativa completa. Integrar esses elementos permitirá que usuários autorizados gerenciem dados reais de RH com regras de acesso aplicadas no backend.

## What Changes

- Integrar a autenticação da aplicação ao Xano e aplicar autorização para operações administrativas.
- Implementar consulta, cadastro, edição e desativação de funcionários usando dados persistidos.
- Implementar a manutenção de departamentos e o vínculo de funcionários a departamentos e cargos.
- Substituir os indicadores demonstrativos do painel por informações obtidas do backend.
- Padronizar a integração HTTP, validações, estados de carregamento, mensagens de erro e feedback de sucesso.
- Preparar as telas administrativas para pesquisa e filtros; oferecer paginação quando suportada pelos endpoints.
- Manter folha de pagamento, cálculos trabalhistas, ponto eletrônico avançado, benefícios e integrações contábeis fora do escopo desta mudança.

## Capabilities

### New Capabilities

- `authentication`: autenticação e autorização de usuários administrativos.
- `employee-management`: consulta e manutenção de funcionários.
- `department-management`: manutenção de departamentos e associação de cargos e funcionários.
- `dashboard`: apresentação de indicadores de RH com dados do backend.

### Modified Capabilities

Nenhuma. O projeto ainda não possui especificações de capacidades registradas.

## Impact

- Interface e estado da aplicação em `Gestao_RH_Impacta/Gestao_RH_Impacta.py`.
- Endpoints e tabelas Xano existentes em `xano/api/rh_api/`, `xano/api/authentication/` e `xano/table/`; contratos e controles de acesso precisam ser confirmados e ajustados conforme necessário.
- Variáveis de ambiente de integração, configuração de execução e testes automatizados.
- O frontend continuará usando Reflex e Python; o Xano continuará responsável pela API, persistência e autorização no backend.
