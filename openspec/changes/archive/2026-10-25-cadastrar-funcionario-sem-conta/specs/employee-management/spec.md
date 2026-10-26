# Spec Delta

## MODIFIED Requirements

### Requirement: Cadastro de funcionário sem conta de acesso
O sistema MUST permitir que um usuário com perfil Gestor RH cadastre um funcionário informando seu nome e selecionando um departamento existente, sem exigir nem criar uma conta de acesso. Cargo e data de admissão podem ser informados; a situação inicial MUST ser “Ativo”. O formulário MUST NOT solicitar nem enviar salário. Após a confirmação do backend, o funcionário MUST aparecer na listagem real de colaboradores.

#### Scenario: Cadastro válido por usuário RH
- **WHEN** um usuário Gestor RH informa o nome do funcionário, seleciona um departamento existente e envia os dados funcionais válidos
- **THEN** o backend persiste o registro sem exigir uma conta de acesso e a listagem apresenta o novo funcionário

#### Scenario: Nome ou departamento inválido
- **WHEN** o nome está vazio ou o departamento selecionado não existe
- **THEN** o backend rejeita o cadastro, não persiste um funcionário parcial e a interface informa o problema

#### Scenario: Falha de validação ou persistência
- **WHEN** os dados são inválidos ou a API não conclui o cadastro
- **THEN** a interface apresenta um erro sem indicar sucesso e preserva os dados preenchidos para correção ou nova tentativa

#### Scenario: Usuário sem perfil Gestor RH
- **WHEN** um usuário sem perfil Gestor RH tenta consultar opções ou cadastrar um funcionário
- **THEN** o backend rejeita a operação e nenhum dado é criado ou alterado

### Requirement: Opções protegidas de departamentos
O backend MUST fornecer os departamentos existentes para o formulário somente a usuários autenticados com perfil Gestor RH. A resposta MUST conter apenas os identificadores e nomes necessários à seleção.

#### Scenario: Gestor RH carrega departamentos
- **WHEN** um usuário Gestor RH abre o formulário de cadastro
- **THEN** a interface apresenta departamentos existentes obtidos do backend e permite informar o nome do funcionário

#### Scenario: Departamentos não autorizados ou indisponíveis
- **WHEN** a sessão é inválida, o perfil não é Gestor RH ou a consulta de opções falha
- **THEN** o backend rejeita a consulta ou a interface apresenta erro, sem exibir opções fictícias
