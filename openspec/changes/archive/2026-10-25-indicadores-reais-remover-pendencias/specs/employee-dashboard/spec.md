# Spec Delta

## Purpose

Esta capacidade define os indicadores apresentados ao RH na página de gestão de colaboradores, usando os registros reais da organização e mantendo o resumo livre de informações demonstrativas ou desnecessárias.

## ADDED Requirements

### Requirement: Indicador real de colaboradores ativos
O sistema MUST apresentar a quantidade real de colaboradores cuja situação seja “Ativo”, calculada a partir dos registros retornados pela API autorizada de colaboradores. Enquanto a listagem estiver carregando ou houver falha na consulta, o sistema MUST indicar esse estado sem apresentar um número demonstrativo ou tratar a falha como zero. Quando a API retornar uma lista válida sem colaboradores ativos, o indicador MUST apresentar zero. Após o cadastro confirmado de um colaborador ativo, o indicador MUST refletir a inclusão sem aguardar uma nova consulta.

#### Scenario: Contagem de colaboradores ativos
- **WHEN** a API retorna colaboradores com situações ativas e não ativas
- **THEN** o indicador apresenta somente a quantidade de registros cuja situação é “Ativo”

#### Scenario: Lista válida sem colaboradores ativos
- **WHEN** a API retorna uma lista válida sem registros com situação “Ativo”
- **THEN** o indicador apresenta zero colaboradores ativos

#### Scenario: Consulta inicial em andamento ou com falha
- **WHEN** a consulta dos colaboradores está carregando ou termina com erro
- **THEN** a interface indica carregamento ou erro e não apresenta um número demonstrativo nem um zero que represente falha

#### Scenario: Cadastro ativo confirmado
- **WHEN** o backend confirma o cadastro de um novo colaborador com situação inicial “Ativo”
- **THEN** o indicador aumenta para refletir o novo registro sem aguardar uma nova consulta

#### Scenario: Colaborador sem conta permanece após atualizar a página
- **WHEN** a listagem autorizada retorna um colaborador cadastrado sem conta de acesso
- **THEN** o colaborador permanece visível após recarregar a página e é incluído na contagem de ativos quando sua situação é “Ativo”

### Requirement: Resumo sem card de pendências
A página de gestão de colaboradores MUST NOT apresentar um card ou seção de pendências. A remoção MUST preservar o indicador de colaboradores ativos, o card “Em férias” existente e as demais áreas não relacionadas da página.

#### Scenario: RH abre a página de gestão de colaboradores
- **WHEN** um usuário acessa a página de gestão de colaboradores
- **THEN** a página apresenta o indicador de colaboradores ativos e o card “Em férias”, sem apresentar card ou seção de pendências
