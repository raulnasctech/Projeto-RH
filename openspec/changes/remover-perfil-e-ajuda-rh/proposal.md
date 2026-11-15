# Proposal

## Why

O painel contém elementos ainda não necessários para a entrega acadêmica: a entrada “Perfil” no menu e um cartão de ajuda que sugere contato com RH. Removê-los simplifica a navegação sem alterar o acesso direto à página de perfil.

## What Changes

- Remover a entrada “Perfil” dos menus laterais do painel e das páginas internas.
- Remover os cartões laterais “Precisa de ajuda?” em todas as variações do menu, incluindo “Suporte RH” e “Fale com o RH”.
- Manter a página e a rota direta `/perfil` acessíveis conforme as regras de autenticação existentes.

## Capabilities

### New Capabilities

- `application-navigation`: define os itens de navegação e os elementos auxiliares apresentados nas barras laterais.

### Modified Capabilities

Nenhuma.

## Impact

- Interface Reflex em `Gestao_RH_Impacta/Gestao_RH_Impacta.py`, nas barras laterais do início e das demais páginas.
- Nenhuma alteração em APIs, autenticação, dependências ou comportamento da rota `/perfil`.
