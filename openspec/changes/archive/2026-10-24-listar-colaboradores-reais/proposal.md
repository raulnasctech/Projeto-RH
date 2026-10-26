# Proposal

## Why

A tela de gestão de colaboradores ainda apresenta nomes, indicadores e situações fixos, que não refletem os registros reais do Xano. Esta mudança conecta a listagem ao backend autorizado para que o perfil de RH consulte os colaboradores cadastrados e veja os nomes relacionados sem confundir dados demonstrativos com dados reais.

## What Changes

- Substituir os registros demonstrativos da lista por resultados do endpoint `GET /employees`.
- Ajustar a resposta do endpoint para incluir o nome do usuário vinculado e o nome do departamento, além dos campos do funcionário necessários à listagem.
- Apresentar estados explícitos de carregamento, lista vazia e erro, sem mostrar dados de demonstração como resultado real.
- Manter a autorização existente no backend; a interface não será tratada como controle de acesso.
- Evitar validações duplicadas de identidade no fluxo imediato de login e listagem, mantendo a validação adicional quando uma consulta for negada.
- Fora do escopo: busca, filtros, paginação, indicadores, cadastro, edição, exclusão e gestão de departamentos.

## Capabilities

### New Capabilities

- `employee-directory`: consulta e apresentação de uma lista real de colaboradores, incluindo os nomes relacionados e os estados de carregamento, vazio e erro.

### Modified Capabilities

Nenhuma.

## Impact

- API Xano `GET /employees` e suas relações com `user` e `departaments`.
- Página de colaboradores, autenticação e estado Reflex, atualmente definidos em `Gestao_RH_Impacta/Gestao_RH_Impacta.py`.
- Integração HTTP e testes automatizados existentes em `Gestao_RH_Impacta/` e `tests/`.
