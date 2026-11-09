# Department Management Specification

## Purpose

Permitir que o Gestor de RH mantenha os departamentos da organização e os disponibilize para associação aos colaboradores.

## Requirements

### Requirement: Gestão de departamentos pelo RH
O sistema MUST permitir que usuários autenticados com perfil Gestor RH listem, cadastrem e editem departamentos. O backend MUST rejeitar operações sem autenticação válida ou sem o perfil Gestor RH. O cadastro e a edição MUST rejeitar nomes vazios, sem persistir alterações inválidas.

#### Scenario: Gestor RH lista departamentos
- **WHEN** um usuário autenticado com perfil Gestor RH consulta os departamentos
- **THEN** o sistema retorna os departamentos existentes com seus identificadores e nomes

#### Scenario: Gestor RH cadastra departamento
- **WHEN** um usuário com perfil Gestor RH cadastra um departamento com nome não vazio
- **THEN** o backend persiste o departamento e a interface o apresenta na lista

#### Scenario: Gestor RH edita departamento
- **WHEN** um usuário com perfil Gestor RH salva um novo nome não vazio para um departamento existente
- **THEN** o backend persiste o novo nome e a interface atualiza a lista

#### Scenario: Nome vazio no cadastro ou edição
- **WHEN** um usuário tenta cadastrar ou editar um departamento sem informar um nome
- **THEN** o backend rejeita a operação e não persiste alterações

#### Scenario: Usuário sem perfil Gestor RH
- **WHEN** uma chamada sem autenticação válida ou de usuário sem perfil Gestor RH tenta consultar ou alterar departamentos
- **THEN** o backend rejeita a chamada e não retorna nem altera dados de departamentos
