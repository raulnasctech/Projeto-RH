# Spec Delta

## Purpose

Definir o cadastro de funcionários vinculados a contas e departamentos já existentes, sem misturar o registro funcional à criação de contas de acesso.

## ADDED Requirements

### Requirement: Cadastro de funcionário com vínculos existentes
O sistema MUST permitir que um usuário com perfil Gestor RH cadastre um funcionário associando-o a uma conta de usuário e a um departamento já existentes. O cadastro MUST NOT criar conta de acesso nem departamento. Cargo e data de admissão podem ser informados; a situação inicial MUST ser “Ativo”. O formulário MUST NOT solicitar nem enviar salário. Após a confirmação do backend, o funcionário MUST aparecer na listagem real de colaboradores.

#### Scenario: Cadastro válido por usuário RH
- **WHEN** um usuário Gestor RH seleciona uma conta e um departamento existentes e envia os dados funcionais válidos
- **THEN** o backend persiste o vínculo e a listagem apresenta o novo funcionário sem criar outra conta ou departamento

#### Scenario: Conta ou departamento indisponível
- **WHEN** a conta ou o departamento selecionado não existe, não está disponível ou já está associado a outro cadastro
- **THEN** o backend rejeita o cadastro, não persiste um funcionário parcial e a interface informa o problema

#### Scenario: Falha de validação ou persistência
- **WHEN** os dados são inválidos ou a API não conclui o cadastro
- **THEN** a interface apresenta um erro sem indicar sucesso e preserva os dados preenchidos para correção ou nova tentativa

#### Scenario: Usuário sem perfil Gestor RH
- **WHEN** um usuário sem perfil Gestor RH tenta consultar opções ou cadastrar um funcionário
- **THEN** o backend rejeita a operação e nenhum dado é criado ou alterado

### Requirement: Opções protegidas para o formulário de cadastro
O backend MUST fornecer as opções de contas ainda não associadas e de departamentos existentes somente a usuários autenticados com perfil Gestor RH. A resposta MUST conter apenas os identificadores e dados de exibição necessários à seleção, sem credenciais ou campos pessoais desnecessários.

#### Scenario: Gestor RH carrega opções de cadastro
- **WHEN** um usuário Gestor RH abre o formulário de cadastro
- **THEN** a interface apresenta contas disponíveis e departamentos existentes obtidos do backend

#### Scenario: Opções não autorizadas ou indisponíveis
- **WHEN** a sessão é inválida, o perfil não é Gestor RH ou a consulta de opções falha
- **THEN** o backend rejeita a consulta ou a interface apresenta erro, sem exibir opções fictícias
