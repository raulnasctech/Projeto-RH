# Tasks

## 1. Indicador real de colaboradores ativos

- [x] 1.1 Substituir o valor fixo pela contagem dos colaboradores carregados cuja situação é “Ativo”; verificar contagens com situações mistas e lista válida sem ativos.
- [x] 1.2 Tratar carregamento e falha sem exibir contagem demonstrativa ou zero enganoso; verificar estados de carregamento e erro da listagem.
- [x] 1.3 Confirmar que um cadastro ativo aparece na contagem após resposta bem-sucedida do backend; verificar teste do fluxo de cadastro.
- [x] 1.4 Tornar opcional a junção entre colaborador e conta na listagem Xano, preservando o nome legado; verificar a alteração pelo teste de contrato do endpoint.
- [ ] 1.5 Publicar a atualização de `employees_GET` no Xano e confirmar que colaboradores sem conta permanecem na resposta e na contagem após recarregar a tela.

## 2. Remoção de pendências e validação

- [x] 2.1 Remover o card “Pendências” mantendo “Em férias” e demais áreas; verificar a composição da página de gestão.
- [x] 2.2 Executar os testes focados de estado e tela e compilar a aplicação Reflex; confirmar testes aprovados e compilação sem erro.
