# Design

## Context

A tela `colaboradores()` em `Gestao_RH_Impacta/Gestao_RH_Impacta.py` contém indicadores e linhas fixas. A sessão autenticada mantém o token no estado Reflex do servidor. O endpoint `GET /employees` já exige autenticação e autorização `Gestor RH`, mas sua consulta retorna os registros da tabela `employees`, cujas relações são `user_id` e `departaments_id`; a tabela de departamentos fornece o campo `nome`.

## Goals / Non-Goals

**Goals:**
- Buscar os funcionários ao abrir a página e representar os estados de consulta separadamente.
- Entregar à tela nomes relacionados e apenas os campos de funcionário necessários à listagem.
- Manter o token no servidor e a autorização efetiva no Xano.

**Non-Goals:**
- Alterar login, cadastro de usuário, autorização já aplicada aos endpoints ou os dados persistidos.
- Acrescentar busca, filtros, paginação, indicadores ou operações de escrita.

## Decisions

- Ajustar `GET /employees` no Xano para compor a resposta com o nome do registro relacionado em `user` e o nome do departamento em `departaments`, mantendo a autorização já existente. A resposta será limitada a identificador, nome do colaborador, departamento, cargo, admissão e situação; salário e outros dados desnecessários não serão enviados. Isso evita expor relações como IDs sem contexto e evita entregar informação salarial à tela. A implementação deve usar os recursos de relacionamento disponíveis no endpoint Xano, em vez de criar uma segunda consulta pública sem autorização.
- Criar um serviço de leitura de funcionários separado do serviço de autenticação. Ele receberá a URL base e o token do estado de sessão, chamará o endpoint protegido e validará a estrutura da resposta. Separar a responsabilidade evita acoplar consulta e mapeamento dos funcionários aos fluxos de login.
- Adicionar ao estado Reflex uma coleção de funcionários e um estado explícito da consulta. A página carregará a coleção ao ser aberta e renderizará carregamento, lista vazia, lista preenchida ou erro de acordo com o resultado; não haverá fallback para as linhas demonstrativas atuais.
- Tratar rejeição de autenticação conforme o fluxo de sessão existente e apresentar a negação de autorização como erro de acesso. Falhas de rede ou do serviço permanecerão erros explícitos, nunca resultados vazios.
- Evitar uma segunda chamada de identidade imediatamente após o login, pois o token e a identidade já foram confirmados nesse fluxo. Na listagem, usar a chamada ao endpoint protegido como validação de sessão e perfil; consultar `/auth/me` somente após uma resposta de acesso negado para distinguir uma sessão ainda válida de uma sessão expirada.
- Testar o serviço com respostas válidas, campos/relações ausentes, lista vazia, erro HTTP e falha de conexão; testar a tela/estado para confirmar os estados e a ausência de dados fixos.

## Risks / Trade-offs

- [A resposta atual do endpoint pode não incluir os objetos relacionados] → Ajustar e validar o contrato do Xano antes de integrar a tela; não inferir nomes a partir de IDs.
- [Uma resposta inesperada pode conter dados ou tipos inválidos] → Validar o formato no serviço e reportar erro, sem produzir uma lista parcial com aparência de sucesso.
- [O endpoint também pode conter campos sensíveis no retorno atual] → Restringir a seleção no backend aos campos definidos para a listagem e verificar o contrato de saída em teste.

## Migration Plan

1. Ajustar o contrato de `GET /employees` para incluir os nomes relacionados e restringir os campos de saída, preservando autorização e compatibilidade com os demais consumidores.
2. Implementar e testar o serviço de leitura e a apresentação dos estados Reflex.
3. Verificar o fluxo com uma conta RH, uma conta sem autorização e uma lista sem registros.
4. Se a implantação da interface precisar ser revertida, restaurar a tela anterior; manter no backend a autorização e a resposta expandida, que não removem campos do contrato existente.
