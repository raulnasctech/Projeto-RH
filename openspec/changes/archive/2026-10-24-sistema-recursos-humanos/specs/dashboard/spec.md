# Spec Delta

## Purpose

Definir o painel inicial de RH como uma visão resumida, atualizada e confiável dos dados de funcionários e departamentos persistidos no backend.

## ADDED Requirements

### Requirement: Indicadores do painel de RH
O sistema MUST apresentar indicadores derivados de dados reais do backend, incluindo total de funcionários ativos, admissões no mês e distribuição por departamento, sem tratar valores demonstrativos como dados reais.

#### Scenario: Indicadores carregados
- **WHEN** o backend retorna os dados necessários para os indicadores
- **THEN** o painel apresenta valores calculados a partir desses dados

#### Scenario: Falha ao carregar indicadores
- **WHEN** uma consulta necessária para os indicadores falha
- **THEN** o painel informa a falha e não apresenta valores fictícios como se fossem atuais

#### Scenario: Backend sem dados para os indicadores
- **WHEN** o backend não possui registros suficientes para calcular um indicador
- **THEN** o painel apresenta um estado vazio ou um valor neutro claramente identificado

### Requirement: Estados de carregamento do painel
O sistema MUST indicar quando os indicadores estão sendo carregados e MUST permitir que o usuário reconheça se os dados exibidos foram obtidos com sucesso.

#### Scenario: Consulta em andamento
- **WHEN** o painel aguarda respostas do backend
- **THEN** a interface apresenta um estado de carregamento até receber sucesso ou falha
