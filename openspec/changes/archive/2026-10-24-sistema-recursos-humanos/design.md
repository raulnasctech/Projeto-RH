# Design

## Context

Ver [proposal.md](./proposal.md) para a motivação e o escopo. A aplicação atual concentra as telas e o estado Reflex em `Gestao_RH_Impacta/Gestao_RH_Impacta.py`; o login chama o Xano, mas as telas administrativas ainda contêm dados demonstrativos. O Xano já possui endpoints e tabelas de usuários, funcionários e departamentos. Os endpoints de funcionários e departamentos existentes precisam ser revistos quanto à autenticação e autorização antes de serem usados em produção.

## Goals / Non-Goals

**Goals:**

- Separar apresentação, estado de tela e acesso aos serviços do Xano de forma incremental e testável.
- Manter o Xano como fonte de verdade para persistência, validação de integridade e autorização.
- Proteger tokens e credenciais e evitar que dados de exemplo sejam confundidos com dados reais.
- Preservar os fluxos atuais que já funcionam enquanto as telas são conectadas aos dados persistidos.

**Non-Goals:**

- Substituir Reflex, Python ou Xano.
- Projetar neste change os domínios de folha de pagamento, benefícios ou ponto eletrônico avançado.
- Criar um cadastro de cargos independente: o modelo Xano existente guarda o cargo como atributo do funcionário.

## Decisions

1. **Manter o Xano como autoridade dos dados e do acesso.** A aplicação Python fará as chamadas ao Xano; o backend validará perfil e permissões em cada operação protegida. A interface pode ocultar ações indisponíveis, mas isso não substitui a autorização no Xano. A alternativa de validar apenas no cliente foi rejeitada por não proteger chamadas diretas à API.

2. **Centralizar a comunicação HTTP em serviços Python compartilhados.** Os serviços terão URL base configurada pelo ambiente, timeout explícito e tratamento consistente de respostas HTTP e falhas de conexão. As telas não construirão URLs nem interpretarão respostas do Xano por conta própria. Isso reduz duplicação e permite testar serviços com respostas simuladas.

3. **Não armazenar tokens de autenticação no `LocalStorage`.** O token será mantido em contexto de sessão no lado servidor, não serializado como estado visível ao navegador, e enviado ao Xano apenas nas requisições autenticadas. Credenciais e tokens não serão registrados em logs nem versionados. A alternativa atual de `LocalStorage` foi rejeitada porque expõe o token ao código executado no navegador.

4. **Desativar funcionários sem apagar o histórico.** A desativação atualizará o estado do registro para inativo, preservando suas relações e informações históricas. Essa decisão usa o campo `status` existente; o endpoint de backend deverá oferecer essa operação sem exigir exclusão física.

5. **Calcular os indicadores a partir dos dados persistidos.** O painel usará funcionários ativos, datas de admissão e departamentos retornados pelo backend. Se a API não fornecer os dados necessários ou a consulta falhar, a interface apresentará carregamento, vazio ou erro, nunca números demonstrativos como resultado válido.

6. **Introduzir a separação modular de forma incremental.** Serviços de autenticação, funcionários e departamentos serão separados da composição das telas Reflex à medida que os fluxos forem conectados. A alternativa de reescrever toda a aplicação antes de habilitar funcionalidades foi rejeitada para limitar o risco e preservar o trabalho existente.

## Risks / Trade-offs

- **Os endpoints atuais de funcionários e departamentos podem não impor autenticação.** → Revisar e aplicar autorização no Xano antes de liberar operações administrativas; chamadas diretas não autorizadas devem ser cobertas por testes.
- **O contrato de autenticação pode não fornecer o perfil necessário à autorização.** → Confirmar o contrato de sessão e identidade no Xano antes de conectar as telas; não confiar em perfil informado pelo cliente.
- **Os endpoints de listagem podem não suportar pesquisa, filtros ou paginação.** → Confirmar e documentar os contratos; implementar no backend o necessário antes de prometer paginação, ou limitar a interface às operações suportadas.
- **Manter tokens somente no servidor pode exigir adaptação do estado atual do Reflex.** → Validar o isolamento entre sessões e a renovação/expiração do token com testes antes da implantação.
- **Os dados existentes podem ter campos opcionais ou valores inconsistentes.** → Validar contratos e apresentar erros de persistência sem descartar os valores digitados pelo usuário.

## Migration Plan

1. Confirmar os contratos e as permissões dos endpoints no Xano e implantar alterações compatíveis com a aplicação atual.
2. Configurar as variáveis de ambiente necessárias sem inserir valores secretos no repositório.
3. Implantar os serviços e telas Reflex que usam os endpoints autenticados; verificar os fluxos de acesso e de manutenção.
4. Remover a dependência de tokens em `LocalStorage` após confirmar que o fluxo por sessão no servidor funciona.
5. Se a nova versão da aplicação apresentar falha, reverter a aplicação Reflex para a versão anterior. Reverter alterações no Xano somente quando forem compatíveis com os dados já gravados; manter operações aditivas e evitar migrações destrutivas.
