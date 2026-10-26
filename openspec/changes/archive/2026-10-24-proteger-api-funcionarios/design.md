# Design

## Context

Ver [proposal.md](./proposal.md). O grupo Xano `rh_api` possui cinco endpoints de funcionários sem declaração de autenticação. O ambiente real usa uma única tabela autenticável `user`, e o campo `role` nessa tabela identifica o perfil. Uma definição local anterior modelava `users` separadamente, mas não corresponde ao ambiente alvo e não será usada por esta change.

## Goals / Non-Goals

**Goals:**
- Garantir a mesma validação de identidade e perfil nos cinco endpoints de funcionários.
- Negar acesso com segurança quando o registro autenticado não existir ou não tiver perfil RH.

**Non-Goals:**
- Alterar o cadastro/login ou permitir que o próprio usuário escolha/atribua seu perfil.
- Proteger endpoints de departamentos ou alterar as páginas Reflex.

## Decisions

- Implementar uma verificação reutilizável no backend Xano: resolver o usuário pelo ID associado ao token e exigir `user.role` exatamente igual a `Gestor RH`. A tabela plural `users` e a correspondência por e-mail não são usadas porque não existem no ambiente real descrito.
- Exigir token Xano nos cinco endpoints e executar a verificação do papel antes de ler ou modificar funcionários. Usuário inexistente, role vazia ou role diferente resulta em acesso negado.
- Não reutilizar a função de hierarquia de roles existente: ela define uma hierarquia `admin/member`, mas esta API exige comparação exata com `Gestor RH`.
- Manter a atribuição de role fora do signup. Um administrador deve atribuir o valor no registro `user` após a criação da conta; nunca confiar em role enviada pelo formulário público.

## Risks / Trade-offs

- [Usuários autenticados sem role Gestor RH perderão acesso aos endpoints] → Confirmar previamente que os operadores autorizados têm `user.role` exatamente igual a `Gestor RH`; manter o comportamento de negação para os demais.
- [O campo `role` pode não existir no ambiente alvo] → Criar/verificar o campo antes de publicar a função e os endpoints, sem permitir que o cadastro público o defina.
- [Roles podem usar grafias diferentes] → Comparar com o valor acordado exato `Gestor RH` e validar os registros antes de ativar a proteção.

## Migration Plan

1. Confirmar que a tabela `user` do ambiente alvo tem o campo `role` e que cada operador autorizado tem esse campo definido como `Gestor RH`.
2. Publicar a checagem compartilhada e habilitar autenticação/autorização nos endpoints cobertos.
3. Validar chamadas autorizadas, não autenticadas, sem perfil e com perfil diferente.
4. Em caso de bloqueio operacional, reverter as alterações dos endpoints e da checagem; não remover nem reatribuir roles como parte do rollback.
