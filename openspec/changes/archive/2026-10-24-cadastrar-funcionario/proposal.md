# Proposal

## Why

A lista de colaboradores já apresenta registros reais, mas a ação “Novo colaborador” ainda não permite cadastrar um vínculo funcional. O RH precisa registrar um funcionário associado a uma conta de usuário e a um departamento já existentes, sem criar contas de acesso nem departamentos nesta etapa.

## What Changes

- Permitir que um usuário autorizado inicie e conclua o cadastro de um funcionário pela tela de colaboradores.
- Selecionar uma conta de usuário e um departamento existentes, e informar os dados funcionais aceitos pelo backend.
- Validar os dados e a autorização no backend antes de persistir o vínculo, sem aceitar campos fora do escopo do cadastro.
- Apresentar carregamento, erros de validação ou persistência e confirmação; após sucesso, atualizar a lista real.
- Disponibilizar ao formulário somente opções de usuário e departamento autorizadas e os dados mínimos necessários para selecioná-las.

Ficam fora desta change: criação de contas de usuário, cadastro ou edição de departamentos, edição e desativação de funcionários, salário e indicadores do painel.

## Capabilities

### New Capabilities

- `employee-management`: cadastro de um funcionário associado a uma conta e a um departamento existentes.

### Modified Capabilities

Nenhuma.

## Impact

- Tela e estado Reflex da página de colaboradores.
- Contrato do endpoint protegido de cadastro de funcionários no Xano e consultas protegidas de opções para o formulário.
- Serviços Python de comunicação com o Xano e testes do formulário, dos serviços e dos contratos de autorização.
