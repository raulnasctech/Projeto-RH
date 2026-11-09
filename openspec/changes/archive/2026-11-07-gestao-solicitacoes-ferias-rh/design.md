# Design

## Context

Ver `proposal.md` para a motivação e `specs/vacation-request-management/spec.md` para o contrato comportamental. O app usa Reflex, integra com o Xano por serviços Python e já possui autorização de Gestor RH implementada nos endpoints de funcionários. A tela atual calcula o indicador de férias a partir do texto do status do funcionário. Os arquivos locais de férias são genéricos, não aplicam autorização RH e usam `dblink`; o schema local também relaciona `approved_by` à tabela `users`, enquanto a autenticação do projeto usa `user`.

## Goals / Non-Goals

**Goals:**

- Adotar um modelo persistente coerente entre tabela, endpoints e interface, incluindo a associação com `user` para registrar quem decidiu.
- Reutilizar os padrões atuais de autenticação, integração com Xano, estados de interface e testes.
- Evitar que uma falha parcial de publicação deixe endpoints ativos sem tabela ou sem proteção.

**Non-Goals:**

- Criar portal, permissões ou fluxo de solicitação para funcionários.
- Introduzir nova tecnologia, dependência ou serviço externo.
- Apagar solicitações como mecanismo de cancelamento ou recuperação de dados que já tenham sido excluídos remotamente.

## Decisions

1. **Tabela e relacionamentos no Xano.** Criar `vacation_requests` quando ausente; se existir, inspecionar dados e ajustar o schema sem apagar registros. Usar `employees_id` como relação obrigatória com `employees`, `start_date` e `end_date` como datas obrigatórias, `status` com os valores `Pendente`, `Aprovada` e `Rejeitada`, `created_at` e `decided_by` como relação opcional com `user`. A relação `decided_by` registra igualmente aprovações e rejeições. Essa modelagem corrige o vínculo obsoleto com `users` e evita usar `approved_by` para representar uma rejeição. Não remover a tabela para recriá-la: se campos atuais precisarem de correção, fazer alteração não destrutiva e preservar registros.

2. **Regras no backend.** Endpoints de listar, criar e decidir devem validar token e perfil `Gestor RH` no Xano, seguindo o padrão usado pela API de funcionários. O backend valida a existência do funcionário, as datas e a transição de estado; não confiar em verificações feitas apenas pela interface. Reutilizar os endpoints locais existentes somente se puderem ser adequados a esse contrato, sem expor `dblink` irrestrito.

3. **Fluxo do RH.** A nova área Reflex permite ao RH selecionar um funcionário e registrar um período; a API define a situação inicial como `Pendente` e não aceita situação ou responsável escolhidos pelo cliente. A listagem apresenta ações de aprovar/rejeitar apenas em solicitações pendentes. Decisões são operações condicionais ao estado `Pendente`, e o backend registra `decided_by` a partir da identidade autenticada. Não incluir exclusão, edição de períodos já decididos, justificativa de rejeição ou autoatendimento.

4. **Indicador calculado por período.** Substituir a contagem baseada no campo de status do funcionário por solicitações `Aprovada` em que `start_date <= hoje <= end_date`. Contar IDs distintos de funcionários para que solicitações simultâneas ou duplicadas não inflem o indicador.

5. **Serviço e falhas explícitas.** Criar ou estender um serviço Python de férias seguindo o tratamento de autenticação, validação de payload e erros dos serviços existentes. A tela deve distinguir carregamento, vazio e falha; erros do Xano não podem ser convertidos em sucesso nem expor o corpo bruto da resposta.

6. **Testes por contrato e comportamento.** Cobrir o schema e a autorização dos endpoints, os casos positivos e negativos de criação/decisão, a transformação das respostas no serviço, os estados da tela e a contagem única do indicador. Executar os testes focados e a compilação Reflex.

## Risks / Trade-offs

- [O workspace pode conter uma tabela parcialmente configurada ou registros existentes] → Inspecionar o estado remoto antes de alterar o schema; preservar os registros e adicionar/corrigir campos de forma não destrutiva.
- [A tabela pode não existir quando os endpoints forem publicados] → Publicar e confirmar primeiro a tabela e suas relações, depois os endpoints e por último a interface.
- [O indicador pode divergir temporariamente de status legado em `employees`] → Tornar solicitações aprovadas a fonte de verdade para o indicador e deixar explícito que dados de férias apagados não serão reconstruídos automaticamente.
- [Uma decisão concorrente pode tentar aprovar e rejeitar a mesma solicitação] → Fazer a atualização no backend somente se a situação atual ainda for `Pendente` e retornar erro quando nenhuma linha elegível for atualizada.

## Migration Plan

1. Consultar o workspace e a branch Xano que serão alvo; confirmar se a tabela existe e se contém registros.
2. Criar a tabela ou aplicar as adequações não destrutivas, verificando as relações com `employees` e `user`.
3. Publicar os endpoints protegidos e testar autenticação, criação, listagem e decisões com perfis autorizados e não autorizados.
4. Publicar o serviço e a interface Reflex, confirmar os estados de erro/vazio e validar o indicador com períodos dentro e fora da data atual.
5. Em rollback, reverter a interface e os endpoints à versão anterior, mantendo a tabela e seus registros. Não excluir a tabela como parte do rollback.
