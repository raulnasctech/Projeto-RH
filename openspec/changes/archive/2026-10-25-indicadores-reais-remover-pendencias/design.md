# Design

## Context

Ver `proposal.md` para a motivação e `specs/employee-dashboard/spec.md` para os comportamentos esperados. A página de gestão já carrega a listagem autorizada de colaboradores e mantém seus registros em estado compartilhado. O formulário de cadastro insere localmente o novo colaborador após sucesso do backend. A consulta Xano de listagem combina colaboradores com usuários relacionados, embora o vínculo de conta seja opcional. O card de ativos usa atualmente um valor fixo, e a grade contém também cards de férias e pendências.

## Goals / Non-Goals

**Goals:**
- Derivar a contagem de ativos da mesma fonte real usada pela listagem.
- Refletir carregamento, erro, lista vazia e inclusão após cadastro sem apresentar contagens fictícias.
- Remover o card de pendências sem alterar os demais cards ou seções.

**Non-Goals:**
- Criar uma API ou consulta separada para métricas.
- Alterar a contagem demonstrativa de férias ou implementar dados reais para esse card.
- Adicionar um total geral de colaboradores ou métricas de admissões.

## Decisions

- **Reutilizar os colaboradores já carregados:** calcular o total de situação exatamente “Ativo” a partir dos dados da listagem autorizada, em vez de adicionar endpoint ou consulta duplicada. Assim o indicador acompanha a fonte existente e também a inclusão otimista somente após confirmação do cadastro.
- **Tornar opcional o relacionamento de usuário na listagem:** usar junção à esquerda para que colaboradores sem conta permaneçam nos resultados, preservando o fallback de nome da conta para registros legados. Uma junção obrigatória contradiz o cadastro funcional sem conta e causa divergência tanto na listagem após recarga quanto no indicador.
- **Representar carregamento e falha sem número enganoso:** usar os estados existentes da consulta para não exibir dados demonstrativos nem converter falha em zero. Zero é exibido apenas quando a consulta válida confirma que não há registros ativos.
- **Retirar apenas o card de pendências:** manter a estrutura e os dados atuais do card “Em férias”, reduzindo o escopo e evitando alterar informações não solicitadas.

## Risks / Trade-offs

- [A lista de colaboradores falhar e o indicador não conseguir ser calculado] → apresentar o estado de erro existente da listagem, sem recorrer a valores fixos ou zero.
- [Registros sem situação ou com valor diferente de “Ativo”] → não contá-los como ativos; preservar a regra simples e compatível com a situação inicial definida no cadastro.

## Migration Plan

1. Atualizar a consulta Xano para preservar colaboradores sem conta e publicar essa versão do endpoint.
2. Atualizar a página para derivar a métrica da listagem real e remover o card de pendências.
3. Validar os estados de contagem, carregamento e falha com testes e compilar a aplicação.
4. Não é necessária migração de dados; a reversão consiste em restaurar a apresentação anterior e, se necessário, a junção original sem alterar os registros.
