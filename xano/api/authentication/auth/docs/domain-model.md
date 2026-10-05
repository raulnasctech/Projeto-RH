# Modelo de Domínio: Sistema de RH

Este documento descreve os conceitos fundamentais do sistema de Recursos Humanos e os seus relacionamentos.

## Funcionário (Colaborador)
Representa uma pessoa que trabalha na empresa e utiliza o sistema.
### Principais informações
- Nome
- Email de contacto / Login
- Cargo ou Função
- Data de admissão

### Relacionamentos
- Um funcionário pode ter um ou vários horários de trabalho atribuídos.
- Um funcionário gera vários registos de assiduidade ao longo do tempo.

## Horário (Turno)
Define o período de trabalho esperado (regras de entrada e saída) para os funcionários.
### Principais informações
- Hora de entrada
- Hora de saída
- Dias da semana aplicáveis
- Carga horária total

### Relacionamentos
- Um horário pode ser atribuído a vários funcionários.
- Serve de base para verificar se o funcionário cumpriu as horas através dos seus registos de assiduidade.

## Registo de Assiduidade (Ponto)
Representa a marcação real do tempo de trabalho do funcionário num determinado dia.
### Principais informações
- Data e hora exata da marcação
- Tipo de registo (Ex: Entrada, Saída, Início de Pausa, Fim de Pausa)
- Justificação (em caso de falta, atraso ou esquecimento)

### Relacionamentos
- Cada registo de assiduidade pertence única e exclusivamente a um funcionário.