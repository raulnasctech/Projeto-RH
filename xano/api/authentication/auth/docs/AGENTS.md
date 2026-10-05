# Instruções para o Agente de IA (AGENTS.md)

Este ficheiro contém as regras operacionais que o agente de Inteligência Artificial deve seguir ao desenvolver o Sistema de Gestão de RH.

## Documentação
- Antes de realizar alterações significativas ou planear novas funcionalidades, consultar obrigatoriamente os documentos de contexto do projeto: `docs/project-overview.md` e `docs/domain-model.md`.

## Desenvolvimento
- O desenvolvimento deve seguir o princípio de fornecer contexto primeiro e desenvolver o sistema de forma incremental.
- Todas as mudanças arquiteturais ou funcionais devem utilizar o OpenSpec.

## Código
- Reutilizar código existente quando apropriado para evitar duplicação.
- Não modificar funcionalidades ou ficheiros não relacionados com a mudança atual sem uma justificativa técnica forte.

## Arquitetura
- Respeitar as tecnologias e arquitetura definidas no projeto (a serem consolidadas no ficheiro de configuração).
- Não introduzir novas bibliotecas, frameworks ou tecnologias alternativas sem perguntar e obter aprovação primeiro.

## Segurança
- As regras de autorização e segurança devem ser aplicadas sempre no backend (ex: garantir que um funcionário comum apenas tem acesso aos seus próprios dados de assiduidade e horários, enquanto o perfil de RH tem acesso global).
- O frontend não deve ser considerado um mecanismo de segurança.

## Frontend
O frontend do projeto deve ser implementado exclusivamente com Reflex.
Utilize os mecanismos próprios do Reflex para componentes, estado, eventos, páginas e interação.
Não introduza outra tecnologia de frontend para substituir ou complementar o Reflex, salvo quando houver uma alteração arquitetural explicitamente aprovada.

## Testes
- As mudanças funcionais devem possuir uma estratégia de verificação clara para assegurar que a implementação corresponde à especificação.