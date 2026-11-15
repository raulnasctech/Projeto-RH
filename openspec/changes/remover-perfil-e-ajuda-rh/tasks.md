# Tasks

## 1. Ajustes de navegação

- [x] 1.1 Remover o item “Perfil” dos menus laterais do início e das páginas internas, mantendo a rota `/perfil`; verificar que a rota continua registrada e que o item não aparece nos menus.
- [x] 1.2 Remover os cartões laterais de ajuda das duas composições de menu; verificar que “Precisa de ajuda?”, “Fale com o RH” e “Suporte RH” não são exibidos em nenhuma barra lateral.

## 2. Verificação

- [x] 2.1 Criar ou ajustar testes focados para os menus e executar a suíte relacionada, confirmando a ausência dos itens removidos e a preservação da rota direta `/perfil`.
- [x] 2.2 Validar os artefatos da mudança com `openspec validate remover-perfil-e-ajuda-rh`.
