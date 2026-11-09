# Promptária

Repositório de instrumentos promptuais reutilizáveis, identificados por título e preservados como unidades independentes.

## Automação de correferência por título

A resolução canônica é implementada por scripts/promptaria_resolver.py e pelo contrato JavaScript em .github/scripts/resolver-correferencia.mjs. O resolvedor consulta o registro operacional config/instrument-registry.json, recupera os arquivos em instruments/*.md e usa o primeiro cabeçalho H1 como título canônico. A correspondência preserva identidades distintas e não encerra a busca na primeira ocorrência.

**Acionamento pelo GitHub:** o workflow manual **Promptária — receber e resolver demanda** recebe um objeto JSON em `request_json`, executa a análise contextual e os handlers especializados selecionados e publica o resultado como artefato. O workflow usa somente `contents: read`: não grava no repositório nem autoriza efeitos externos. O comando de comentário `/promptaria merge <SHA>` continua restrito à aprovação explícita de integração de pull requests, descrita abaixo.

### Adicionar um instrumento

1. Crie um arquivo Markdown em instruments/.
2. Use o título oficial no primeiro cabeçalho H1.
3. Preserve integralmente o conteúdo e as instruções próprias.
4. Atualize o registro, os catálogos e os manifestos correspondentes.
5. Execute os testes e validadores antes de integrar a alteração.

## O que está automatizado

- **Recepção e resolução contextual de demandas:** .github/workflows/promptaria-receber-demanda.yml recebe `request_json`, carrega a pré-configuração contínua integral, executa o roteamento contextual e os handlers selecionados e publica um artefato auditável, sem permissões de escrita.
- **Verificação de pull requests:** .github/workflows/promptaria-tests.yml executa o contrato JavaScript, as salvaguardas dos workflows privilegiados e a suíte Python.
- **Classificação de novos instrumentos:** .github/workflows/auto-enable-new-promptual-instruments.yml chama scripts/auto_enable_new_promptual_instruments.py. Títulos novos contendo “Instrumento promptual” são classificados como recuperáveis sob demanda por padrão; automação contínua exige a declaração expressa prevista na política.
- **Integração controlada:** .github/workflows/promptaria-integracao-pr.yml valida o comentário exato /promptaria merge <SHA> em uma pull request própria, aberta e destinada a main; não faz o merge.
- **Auto-merge protegido:** .github/workflows/promptaria-auto-merge.yml só integra o SHA testado após checks concluídos com sucesso e aprovação explícita do proprietário para aquele SHA exato.

## Limites importantes

Esta versão gera um **plano validável**, não executa magicamente as instruções de cada prompt. Não lê conversas arbitrárias do ChatGPT, não conecta automaticamente o GitHub ao conector do ChatGPT e não escreve em Nocturna ou em outros repositórios. A demanda precisa ser transmitida por um evento descrito acima; execução externa exige integração e permissões próprias.

A decisão semântica sobre função diversa não é reduzida a uma heurística lexical: o resultado marca a exceção como pendente de revisão contextual. O workflow não declara executada uma operação quando apenas identificou um título.

## Execução local

```bash
python scripts/promptaria_resolver.py --request request.json --instruments instruments --output promptaria-result.json
python -m unittest discover -s tests -v
```

O arquivo de entrada deve conter JSON com `request` e, opcionalmente, `destination` e `dry_run`.

## Protocolo-mestre e préconfiguração padrão

O instrumento `instruments/protocolo-mestre-acionamento-automatico.md` preserva o modelo genérico com seus quatro elementos estruturais e serve como préconfiguração para demandas futuras. O resolvedor inclui automaticamente, em cada plano, os três componentes-base: a arquitetura coordenadora, o protocolo-mestre e o instrumento operacional do GitHub. Títulos adicionais mencionados são todos recuperados por correspondência normalizada.

`github-operational-recoverable` permanece como extensão contínua interna. A instância preexistente `github-operational-demand-mirror` foi transferida efetivamente para `continuous_automation`, preservando seu ID e arquivo. A nova contraparte `github-operational-demand` foi criada e registrada exclusivamente em `recoverable_on_demand`, com ID, arquivo e handler próprios. As fases mantêm referências recíprocas, sem pertencimento simultâneo, exposição cruzada ou ativação recuperável pela mera presença do contexto contínuo.

A inclusão automática é uma préconfiguração de reconhecimento e planejamento, não uma alegação de que as instruções especializadas foram executadas. O resolvedor rejeita `dry_run` que não seja booleano JSON; o padrão é `true`. A escrita é tratada por um executor separado e nunca é disparada apenas porque um título ou prompt foi recuperado. No workflow GitHub Actions, a integração do executor é deliberadamente restrita à simulação; escrita real não é autorizada pelo workflow. Exceções semânticas de função diversa exigem revisão contextual; o resolvedor não as decide por mera comparação lexical.

Não há acionamento geral de demandas por comentário nem workflow manual de resolução de demandas. O comando `/promptaria merge <SHA>` é exclusivo para aprovação explícita de integração de uma pull request própria destinada a `main`; ele não executa a demanda nem aciona instrumentos. Para resolver uma demanda, use localmente o comando do resolvedor Python mostrado na seção anterior e valide o artefato com a suíte de testes.

## Pré-configuração de sincronização do catálogo e sitemap

O instrumento `instruments/preconfiguracao-sincronizacao-catalogo-sitemap.md` agora é incluído automaticamente em todos os planos do resolvedor quando o arquivo está presente. Ele incorpora os elementos estruturais do modelo de sincronização fornecido, mas condiciona sua aplicação à existência confirmada da árvore `Promptária/`, de `manifest.json`, de `sitemap.xml` e da configuração de publicação correspondente. Isso evita criar uma segunda fonte canônica: a arquitetura vigente baseada em `instruments/*.md`, no resolvedor Python, no executor separado e na auditoria permanece preservada.

A pré-configuração é idempotente por princípio, exige validação antes de alterações e distingue recuperação/inclusão no plano de execução real. O workflow de resolução continua em modo de simulação para operações do executor e com permissões de leitura; nenhuma autorização de escrita real foi acrescentada.

## Cadeia de integridade da auditoria

Os novos registros incluem `audit_prev_hash` e `audit_hash`, calculados a partir de JSON canônico. O executor verifica a cadeia disponível e bloqueia alterações detectáveis, reordenação, JSON inválido e última linha incompleta. **Uma cadeia local, isoladamente, não consegue detectar com garantia a remoção de um sufixo completo nem a substituição integral do arquivo.** Registros legados sem hash só podem aparecer antes do início da cadeia; o primeiro registro encadeado ancora os bytes do histórico anterior, mas não protege contra truncamento posterior sem uma âncora externa. Operações de escrita real agora registram `write_intent` antes da mutação e `executed` após a validação; se a conclusão desaparecer ou a execução for interrompida, a reutilização do mesmo `operation_id` falha fechada e exige reconciliação manual. Para detectar remoção de histórico, exporte periodicamente âncoras para armazenamento externo confiável, protegido contra alteração pela identidade do executor.

## Validação de resultados e testes de regressão

Após a resolução, `scripts/promptaria_validate_result.py` verifica o contrato do artefato: esquema esperado, presença dos três componentes obrigatórios, recuperação de conteúdo, estados que não alegam execução e indisponibilidade de escrita no resolvedor. A validação falha de forma explícita se faltar qualquer componente obrigatório ou se o JSON declarar uma execução que não ocorreu.

O workflow `.github/workflows/promptaria-tests.yml` executa a suíte de regressão e um smoke test com os instrumentos reais do repositório: chama o resolvedor e valida o JSON resultante. A suíte também verifica integridade da coleção real de instrumentos, caminhos distintos, preservação de instrumentos distintos que compartilham um título normalizado, presença dos componentes-base, recusa de correspondência por título parcial e o contrato que impede alegações falsas de execução. Assim, a integração verifica tanto fixtures de teste quanto os instrumentos versionados.

## Âncora externa da auditoria

A cadeia local detecta alterações dentro do histórico disponível, mas não consegue provar que um sufixo completo não foi removido. O utilitário `scripts/promptaria_audit_anchor.py` permite criar e verificar um checkpoint do prefixo da cadeia. O arquivo de âncora deve ficar fora do repositório, em armazenamento com controles de acesso independentes e permissões que impeçam a identidade do executor de alterá-lo ou removê-lo. Apenas usar outra pasta no mesmo diretório ou no mesmo domínio de permissões **não** cria uma fronteira de confiança.

```bash
python scripts/promptaria_audit_anchor.py --mode create \
  --audit .promptaria/audit.jsonl \
  --anchor /caminho/externo-protegido/promptaria-anchor.json \
  --repo-root .

python scripts/promptaria_audit_anchor.py --mode verify \
  --audit .promptaria/audit.jsonl \
  --anchor /caminho/externo-protegido/promptaria-anchor.json \
  --repo-root .
```

Crie âncoras em uma rotina confiável após operações ou em intervalos definidos, e verifique-as antes de aceitar o histórico. A verificação permite acréscimos posteriores, mas falha se o prefixo protegido estiver ausente ou divergente. A ferramenta não provisiona armazenamento externo nem administra credenciais; isso deve ser configurado operacionalmente.

## Executor especializado com permissões e auditoria

O executor `scripts/promptaria_executor.py` é uma etapa separada do resolvedor: reconhecer um instrumento ou incluí-lo no plano nunca executa seu conteúdo. O executor aceita apenas a operação estruturada `write_text`; não interpreta prompts recuperados como comandos nem executa shell.

- O padrão é `dry_run: true`; a simulação não grava o destino.
- A execução real exige simultaneamente `dry_run: false`, `write_authorized: true` e `--confirm-operation` com o mesmo `operation_id` da solicitação.
- `config/promptaria_permissions.json` limita a escrita a arquivos sob `artifacts/` e impõe limite de tamanho.
- O destino é validado como caminho relativo POSIX, com proteção contra traversal, `.git`, caminhos absolutos, links simbólicos e arquivos não regulares. A travessia, a criação de diretórios, a substituição e a verificação do resultado usam descritores de diretório e operações relativas ao diretório-pai, com `O_NOFOLLOW` quando suportado.
- A escrita autorizada é atômica e o executor compara o SHA-256 do conteúdo solicitado com o resultado gravado.
- Cada operação aceita é registrada em `.promptaria/audit.jsonl`, com identificador, modo, destino, estado e hashes. Escritas reais registram intenção antes da mutação e conclusão depois; uma intenção sem conclusão bloqueia a repetição do mesmo identificador e exige reconciliação manual.
- O executor abre `.promptaria` relativamente a um descritor da raiz e mantém o descritor do diretório de estado aberto durante a operação. `audit.jsonl` e `executor.lock` são abertos relativamente a esse descritor, com `O_NOFOLLOW` quando disponível; a auditoria é lida e anexada pelo mesmo descritor fixado, com `flock`, verificação de identidade do inode e `fsync`. O diretório é restringido a `0700`, e os arquivos de estado a `0600`, apertando permissões legadas quando pertencem ao usuário executor.

Exemplo de solicitação de simulação:

```json
{
  "operation_id": "relatorio-2026-001",
  "operation": "write_text",
  "destination": "artifacts/relatorio.txt",
  "content": "Conteúdo a validar.\n"
}
```

Execute com `python scripts/promptaria_executor.py --request request.json --repo-root .`. Para uma escrita real, altere explicitamente os dois campos de autorização no JSON e forneça `--confirm-operation relatorio-2026-001`. Use apenas após revisar o conteúdo e o destino. Testes: `python -m unittest discover -s tests -v`.

**Limite do modelo de ameaça:** estas medidas protegem contra outros usuários locais e reduzem as corridas de substituição de caminhos; `flock` é consultivo e só serializa participantes cooperantes. Um processo hostil executando sob a mesma identidade/UID do executor pode, em geral, agir com os mesmos privilégios sobre esses arquivos e diretórios. Para resistência contra comprometimento da mesma identidade, execute o executor sob uma conta dedicada com permissões mínimas e mantenha a âncora de auditoria em um domínio de controle independente. A auditoria e a mutação do destino também não formam uma única transação atômica.

### Integração do executor no workflow

No evento manual **Actions → Run workflow**, o campo opcional `executor_request_json` aceita um objeto JSON com `operation_id`, `operation`, `destination` e `content`. Quando fornecido, o workflow prepara a solicitação e chama `scripts/promptaria_executor.py`; os resultados de resolução e a auditoria da simulação são publicados como artefatos separados.

**Proteção no CI:** o preparador força `dry_run: true` e `write_authorized: false`, ignorando qualquer tentativa de incluir flags de autorização no JSON de entrada. Comentários `/promptaria` continuam limitados à resolução. O workflow mantém permissões `contents: read` e não grava alterações no repositório. A execução real, quando necessária, deve ocorrer fora desse fluxo de CI e exigir a confirmação explícita prevista no executor.

Exemplo para o campo `executor_request_json`:

```json
{
  "operation_id": "relatorio-2026-001",
  "operation": "write_text",
  "destination": "artifacts/relatorio.txt",
  "content": "Conteúdo a validar.\\n"
}
```

O pedido acima será apenas simulado pelo workflow, mesmo se forem acrescentados `"dry_run": false` ou `"write_authorized": true`. Testes adicionais do preparador: `python -m unittest tests.test_promptaria_prepare_executor_request -v`.


## Préconfiguração de demandas estruturadas (schema 2.3)

O resolvedor também aceita `request` como objeto JSON estruturado. Para preservar a informação, campos como `operation`, `demand`, `source`, `transformation`, `destinations`, `validation`, `production_chain`, `navigation_invariants` e `status` são mantidos no `operation_context` do resultado quando fornecidos. Textos operacionais e listas relevantes são usados para correferência por título sem remover a estrutura original.

A configuração trata números de catálogo, caminhos, estados e auditorias incorporados em modelos como dados declarados que precisam ser comparados ao estado real do repositório. Não assume que caminhos de um exemplo existam aqui, nem que fotografias históricas descrevam o catálogo ativo. Antes de qualquer mutação, o executor deve confirmar a árvore, identificar conflitos, validar autorização e caminhos, preservar os arquivos existentes e verificar a integridade depois da gravação. A automação continua em modo de simulação por padrão; identificar instrumentos não significa executá-los.


## Execução especializada dos instrumentos

Os IDs do manifesto e seus handlers especializados são mapeados em config/instrument-execution-map.json. A execução especializada é uma etapa local separada da resolução por título: recuperar um instrumento ou incluí-lo num plano não executa seu conteúdo. Use os scripts em scripts/ conforme os contratos descritos em docs/execucao-especializada-instrumentos.md; não há atualmente um workflow GitHub Actions de execução especializada. Títulos que colidem após normalização exigem desambiguação por ID. Os handlers não executam código arbitrário contido nos instrumentos.

## Análise contextual cumulativa e seleção funcional de tarefas

A camada de análise contextual é implementada por scripts/promptaria_context_router.py e scripts/promptaria_contextual_executor.py. Ela combina os elementos-base com as evidências circunstanciais da demanda — ações, objeto, finalidade, títulos, IDs, caminhos e campos estruturados — e registra a proveniência da seleção.

A seleção contextual é cumulativa, mas não funde identidades nem concede autorização de escrita. A execução é local e depende do executor especializado, das permissões e das validações correspondentes; não existe um workflow GitHub Actions ativo que execute essa etapa.

## Protocolo de atualização integral e preservação funcional

O protocolo de atualização e preservação foi separado do conjunto operacional e está arquivado em auxiliary-protocols/protocolo-operacional-atualizacao-integridade-acervo.md, com registro em auxiliary-protocols/registry.json. Ele não integra o manifesto, o catálogo operacional nem a seleção automática.

A recuperação é explícita, por ID ou título, usando python scripts/resolve_auxiliary_protocol.py --id protocol-update-integrity ou --title "PROTOCOLO OPERACIONAL DE ATUALIZAÇÃO, REINTEGRAÇÃO E PRESERVAÇÃO FUNCIONAL DO ACERVO DE INSTRUMENTOS PROMPTUAIS DO PROMPTÁRIA". O protocolo auxiliar permanece habilitado em seu próprio registro, sem se tornar membro operacional nem ser pré-carregado em todos os planos.

## Instrumento Nocturna: arquitetura da necessidade e identidade sistêmica

O instrumento `instruments/nocturna-arquitetura-necessidade-identidade-sistemica.md` foi adicionado com o título canônico completo, ID `nocturna-arquitetura-necessidade-identidade-sistemica`, nó de interface `instrument:nocturna-arquitetura-necessidade-identidade-sistemica` e referências no registro, catálogo e manifesto de integridade. Seu método cobre inventário de proveniência dos acervos Nocturna, seleção estrutural, reconstrução recursiva, objeções encadeadas, indução fractal como analogia relacional, norma representacional Logos, distinção de estatutos epistêmicos e verificação de não contradição.

O resolvedor inclui o instrumento em planos futuros como `mandatory_nocturna_architecture_preconfiguration`, sem alegar execução nem acesso automático ao repositório externo Nocturna. A análise das coleções e publicações só pode ser declarada concluída quando as fontes estiverem efetivamente acessíveis e verificadas. A inclusão no catálogo não substitui esse acesso nem converte hipóteses em fatos.

## Pré-configuração obrigatória de rastreabilidade para novos instrumentos

O workflow .github/workflows/promptaria-tests.yml verifica pull requests com testes de contrato JavaScript, salvaguardas de integração privilegiada e a suíte Python completa. A validação de identidade e caminhos também possui utilitários locais em scripts/validate_instrument_registry.py e scripts/validate_instrument_reference_contract.py.

Para cada instrumento, preserve o primeiro H1 como título canônico e mantenha ID, caminho, aliases, funções, relações, operações e nó de interface coerentes no registro. O manifesto raiz manifest.json e o manifesto de testes tests/manifest.json devem representar a mesma identidade e os mesmos caminhos. A validação estrutural não executa o conteúdo dos instrumentos nem autoriza escrita.

## Ativação funcional explícita e inclusão futura

O registro operacional config/instrument-registry.json é a fonte de verdade para a ativação por título. Na árvore atual ele contém oito instrumentos operacionais; a recuperação do protocolo de integridade permanece separada no registro auxiliar. A flag activation.enabled controla a resolução funcional e a visibilidade operacional. Presença no diretório ou no manifesto, isoladamente, não concede autorização para executar efeitos externos.

## Ativação controlada e pré-configuração futura

O workflow .github/workflows/auto-enable-new-promptual-instruments.yml chama scripts/auto_enable_new_promptual_instruments.py para classificar apenas entradas novas em relação ao SHA-base do pull request. A regra vigente é:

- Título canônico novo contendo “Instrumento promptual”: category recoverable_on_demand, classification_basis default_title_rule, activation.mode on_demand_title, habilitado e visível para recuperação explícita por título.
- Exceção: somente a declaração exata <!-- promptaria: continuous_automation: explicit --> no arquivo-fonte classifica o instrumento como continuous_automation; ele permanece desabilitado e sem executor até configuração e autorização separadas.
- Instrumentos já existentes na branch-base não são recategorizados nem reativados por essa rotina.

A rotina sincroniza a classificação e sua proveniência nos registros, catálogos e manifestos espelhados. Recuperabilidade sob demanda não significa execução automática nem autorização de efeitos colaterais. Consulte docs/politica-classificacao-instrumentos-promptuais.md.

## Classificação prévia da demanda: correferência ou automação distinta

O roteador contextual local scripts/promptaria_route_request.py distingue referências a instrumentos, pedidos de pré-configuração, intenções mistas, referências inativas ou não registradas e demandas que exigem revisão contextual. Essa classificação não é executada por um workflow GitHub Actions de recepção de demandas. Ela não substitui o resolvedor, não ativa instrumentos e não autoriza mutações.

O registry é a autoridade para acionamento por título. A classificação semântica deve preservar a distinção entre correferência funcional, automação distinta e atribuição explícita de função diversa.

## Manutenção da documentação

O script `scripts/sync_readme_inventory.py` sincroniza automaticamente as seções de inventário do README com os diretórios versionados. O workflow de classificação de novos instrumentos executa essa sincronização antes de publicar alterações de metadados e inclui o README no mesmo commit. Para outras alterações estruturais, execute `python scripts/sync_readme_inventory.py`; use `--check` para verificar se o inventário está atualizado sem conservar alterações.

## Inventário versionado — conferido com a árvore de main

### Instrumentos operacionais (11)

- `instruments/acione-a-promptaria-pelo-github.md`
- `instruments/arquitetura-unificada-acionamento-correferencia-recuperacao-aplicacao.md`
- `instruments/github-operational-demand-mirror.md`
- `instruments/github-operational-demand.md`
- `instruments/github-operational-recoverable.md`
- `instruments/modelo-instrumento-promptual-correferencia.md`
- `instruments/nocturna-arquitetura-necessidade-identidade-sistemica.md`
- `instruments/preconfiguracao-correspondencia-futura-e-cadeia.md`
- `instruments/preconfiguracao-sincronizacao-catalogo-sitemap.md`
- `instruments/protocolo-mestre-acionamento-automatico.md`
- `instruments/protocolo-mestre-execucao-correta.md`

### Scripts Python (23)

- `scripts/activate_instrument.py`
- `scripts/auto_enable_new_promptual_instruments.py`
- `scripts/generate_instrument_catalog.py`
- `scripts/promptaria_audit_anchor.py`
- `scripts/promptaria_audit_inventory.py`
- `scripts/promptaria_context_router.py`
- `scripts/promptaria_contextual_executor.py`
- `scripts/promptaria_execute_preconfigured.py`
- `scripts/promptaria_executor.py`
- `scripts/promptaria_interconnection.py`
- `scripts/promptaria_operation_guard.py`
- `scripts/promptaria_operational_audit.py`
- `scripts/promptaria_preflight.py`
- `scripts/promptaria_prepare_executor_request.py`
- `scripts/promptaria_registry_audit.py`
- `scripts/promptaria_resolver.py`
- `scripts/promptaria_route_request.py`
- `scripts/promptaria_specialized_executor.py`
- `scripts/promptaria_validate_result.py`
- `scripts/resolve_auxiliary_protocol.py`
- `scripts/sync_readme_inventory.py`
- `scripts/validate_instrument_reference_contract.py`
- `scripts/validate_instrument_registry.py`

### Workflows do GitHub Actions (5)

- `.github/workflows/auto-enable-new-promptual-instruments.yml`
- `.github/workflows/promptaria-auto-merge.yml`
- `.github/workflows/promptaria-integracao-pr.yml`
- `.github/workflows/promptaria-receber-demanda.yml`
- `.github/workflows/promptaria-tests.yml`

### Documentação (7)

- `docs/auditoria-operacional-inicial.md`
- `docs/checklist-reconstrucao-workflows.md`
- `docs/contrato-resolvedor-correferencia-js.md`
- `docs/execucao-especializada-instrumentos.md`
- `docs/interconexao-funcional-entre-segmentos.md`
- `docs/politica-classificacao-instrumentos-promptuais.md`
- `docs/preconfiguracao-protocolo-mestre-e-correferencia.md`

### Testes (42)

- `tests/fixtures/correference-parity.json`
- `tests/manifest.json`
- `tests/resolver-correferencia.test.mjs`
- `tests/test_activation_executor_evidence.py`
- `tests/test_auto_enable_new_promptual_instruments.py`
- `tests/test_auxiliary_interface.py`
- `tests/test_auxiliary_protocols.py`
- `tests/test_canonical_artifact_integrity.py`
- `tests/test_context_router_activation_gate.py`
- `tests/test_correfencia_execution_bundle.py`
- `tests/test_github_operational_pair.py`
- `tests/test_instrument_catalog.py`
- `tests/test_instrument_reference_contract.py`
- `tests/test_interface_traceability.py`
- `tests/test_preconfigure_new_instruments.py`
- `tests/test_promptaria_audit_report.py`
- `tests/test_promptaria_contextual_ambiguity_guard.py`
- `tests/test_promptaria_contextual_e2e.py`
- `tests/test_promptaria_contextual_executor.py`
- `tests/test_promptaria_corref.py`
- `tests/test_promptaria_execute_preconfigured.py`
- `tests/test_promptaria_execution_map.py`
- `tests/test_promptaria_executor.py`
- `tests/test_promptaria_functional_preconfiguration.py`
- `tests/test_promptaria_interconnection.py`
- `tests/test_promptaria_inventory_audit.py`
- `tests/test_promptaria_operational_audit.py`
- `tests/test_promptaria_operational_audit_integrity.py`
- `tests/test_promptaria_preflight.py`
- `tests/test_promptaria_prepare_executor_request.py`
- `tests/test_promptaria_registry_audit.py`
- `tests/test_promptaria_repository_integrity.py`
- `tests/test_promptaria_resolver.py`
- `tests/test_promptaria_route_request.py`
- `tests/test_promptaria_specialized_executor.py`
- `tests/test_promptaria_validate_result.py`
- `tests/test_promptaria_workflow_integrity.py`
- `tests/test_resolver_contract.py`
- `tests/test_traceability_context_router.py`
- `tests/test_traceability_preconfiguration.py`
- `tests/teste-cadeia-navegacional.mjs`
- `tests/teste-registro-instrumentos.py`

### Configurações JSON (14)

- `config/continuous-automation-catalog.json`
- `config/cross-segment-interconnection.json`
- `config/instrument-catalog.json`
- `config/instrument-execution-map.json`
- `config/instrument-interconnections.json`
- `config/instrument-reference-contract.json`
- `config/instrument-registry.json`
- `config/interface-traceability-current.json`
- `config/interface-traceability.json`
- `config/promptaria_permissions.json`
- `config/recoverable-on-demand-catalog.json`
- `config/segment-integration-policy.json`
- `config/traceability-graph-current.json`
- `config/traceability-graph.json`

<!-- PROMPTARIA-README-AUTO:END -->


## Catálogos separados por modalidade

O registro canônico mantém as duas fases como identidades distintas. O inventário agregado `config/instrument-catalog.json` reúne todas as entradas apenas para auditoria e cobertura documental; ele não é o catálogo público de seleção. Os catálogos operacionais são separados e gerados por `scripts/generate_instrument_catalog.py`:

- `config/continuous-automation-catalog.json` e `continuous-automation-catalog.json`: instrumentos da categoria `continuous_automation`, incluindo `github-operational`.
- `config/recoverable-on-demand-catalog.json` e `recoverable-on-demand-catalog.json`: instrumentos da categoria `recoverable_on_demand`, incluindo `github-operational-recoverable`, sem listar o instrumento contínuo.

A interface pública carrega exclusivamente `recoverable-on-demand-catalog.json`. Assim, o instrumento antigo permanece na automação funcional contínua, enquanto somente o novo instrumento aparece na recuperação sob demanda.

## Workflows ativos

A árvore atual contém cinco workflows versionados:

- .github/workflows/promptaria-tests.yml: executa os testes de contrato JS, as salvaguardas dos workflows privilegiados e os testes Python em pull requests.
- .github/workflows/promptaria-receber-demanda.yml: recebe demandas JSON por workflow_dispatch, executa o executor contextual e os handlers selecionados e publica o resultado como artefato; mantém contents: read.
- .github/workflows/auto-enable-new-promptual-instruments.yml: aplica a política de classificação de instrumentos novos, com comparação ao SHA-base.
- .github/workflows/promptaria-integracao-pr.yml: recebe comentários de aprovação em pull requests e valida o SHA exato; para PR em rascunho, pode marcá-la como pronta, e para PR não rascunho pode repetir ou aguardar os checks daquele SHA.
- .github/workflows/promptaria-auto-merge.yml: só considera execuções bem-sucedidas de Promptária PR Checks originadas por pull request e exige aprovação OWNER exata antes do merge.

O workflow de recepção é manual por `workflow_dispatch`; não há acionamento genérico por comentário. A execução especializada é feita pelo executor contextual dentro desse fluxo, e não por um segundo workflow separado. A pré-configuração contínua é carregada como contexto inerte, não como handler.

## Integração automática de pull requests

O auto-merge não é irrestrito nem automático apenas porque os checks passaram. A pull request deve estar aberta, destinada a main, originar-se do próprio repositório e não estar em rascunho. Todos os check-runs do SHA testado devem estar concluídos com sucesso, e o proprietário deve publicar o comentário exato /promptaria merge <SHA-testado>. O workflow confere novamente que o HEAD da PR continua igual ao SHA testado e usa merge squash fixado nesse commit.

O workflow de integração por comentário não faz merge: ele valida a aprovação exata e prepara ou reexecuta os checks. Não contorne essa exigência por uma chamada manual de merge.

## Processo de integração

O fluxo de integração é branch → pull request → checks → aprovação explícita do SHA → merge squash. O SHA aprovado deve ser exatamente o mesmo que passou pelos checks. Alterações posteriores invalidam a aprovação anterior e exigem nova validação e novo comentário. As proteções e permissões do GitHub continuam prevalecendo.