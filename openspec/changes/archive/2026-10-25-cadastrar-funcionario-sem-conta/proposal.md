# Proposal

## Why

A listagem de colaboradores demorava a ficar disponível e não refletia imediatamente um cadastro concluído. Além disso, o fluxo exigia associar cada colaborador a uma conta de acesso existente, embora o cadastro funcional do RH deva poder existir independentemente do acesso ao sistema.

## What Changes

- Permitir que o RH cadastre um colaborador informando o nome e selecionando um departamento, sem criar ou associar uma conta de acesso.
- Manter os colaboradores já exibidos durante uma atualização da listagem, distinguindo carregamento, lista vazia e falha.
- Após a confirmação do backend, inserir o colaborador cadastrado na listagem sem aguardar uma nova consulta.
- Preservar autorização no backend e compatibilidade de leitura com registros antigos associados a contas.
- Fora do escopo: criar credenciais ou contas de acesso para colaboradores, incluir salário no formulário ou alterar os processos de autenticação.

## Capabilities

### New Capabilities

### Modified Capabilities

- `employee-management`: permitir cadastro funcional nominal sem conta e fornecer opções protegidas de departamento.
- `employee-directory`: preservar os dados visíveis durante atualização e refletir imediatamente um cadastro confirmado, mantendo a listagem real e estados de erro apropriados.

## Impact

- Interface Reflex e serviço de colaboradores: formulário sem seleção de conta, validação do nome e atualização da lista após confirmação.
- API e persistência Xano: campo nominal no registro funcional, endpoint protegido de opções de departamentos e compatibilidade com registros antigos vinculados a contas.
- Specs e testes de gestão e listagem de colaboradores.
