# Promptária

Repositório de instrumentos promptuais reutilizáveis, identificados por título e preservados como unidades independentes.

## Automação de correferência por título

O workflow `.github/workflows/promptaria-correfencia.yml` permite enviar uma demanda em Actions → Run workflow ou por comentário em uma issue usando `/promptaria <demanda completa com os títulos dos instrumentos>`.

O workflow procura arquivos Markdown em `instruments/`. O primeiro cabeçalho Markdown (`# Título do instrumento`) é o título canônico. A comparação normaliza maiúsculas/minúsculas, Unicode e pontuação e conserva todas as correspondências, sem parar na primeira.

### Adicionar um instrumento

1. Crie um arquivo `.md` em `instruments/`.
2. Coloque o título oficial no primeiro cabeçalho.
3. Preserve o conteúdo integral e as instruções próprias nesse arquivo.
4. Mencione o título na demanda enviada ao workflow.

O componente fixo obrigatório é **Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas**. Se não existir como arquivo Markdown em `instruments/`, o relatório registra a falha em vez de inventar conteúdo.

## O que está automatizado

- Recepção explícita de demanda por evento GitHub autorizado.
- Descoberta de todos os instrumentos Markdown com cabeçalho de título.
- Correspondência por título normalizado, sem limite numérico codificado.
- Inclusão dos componentes-base obrigatórios quando os arquivos existem.
- Validação estrita de destino relativo: bloqueia caminhos absolutos, segmentos `..`, segmentos vazios, `.`, `.git`, separadores Windows e caracteres de controle.
- Validação estrita de `dry_run` e autorização explícita para qualquer pedido de modo não simulado.
- Artefato JSON com correspondências e estados de rastreabilidade.
- Testes de integridade do repositório para conteúdo Markdown não vazio, títulos normalizáveis, caminhos distintos, preservação de instrumentos com títulos equivalentes, presença dos três componentes-base e validade do contrato do resultado.

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

A inclusão automática é uma préconfiguração de reconhecimento e planejamento, não uma alegação de que as instruções especializadas foram executadas. O resolvedor rejeita `dry_run` que não seja booleano JSON; o padrão é `true`. A escrita é tratada por um executor separado e nunca é disparada apenas porque um título ou prompt foi recuperado. No workflow GitHub Actions, a integração do executor é deliberadamente restrita à simulação; escrita real não é autorizada pelo workflow. Exceções semânticas de função diversa exigem revisão contextual; o resolvedor não as decide por mera comparação lexical.

Para acionar uma demanda por comentário, use `/promptaria <demanda completa>` em uma issue. Para execução manual, abra Actions → “Promptária - correferência funcional por título” → Run workflow. O artefato JSON indica componentes obrigatórios ausentes, títulos reconhecidos e estados de rastreabilidade.

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

Os IDs do manifesto e seus handlers especializados são mapeados em `config/instrument-execution-map.json`; o novo protocolo de atualização é uma pré-configuração de planejamento e não declara um handler especializado inexistente. O dispatcher verifica títulos canônicos e hashes das fontes antes de executar as rotinas específicas. Para executar via GitHub Actions, use **Promptária — execução especializada**; os resultados JSON são publicados como artefatos. Títulos que colidem após normalização exigem `instrument_ids` explícitos. Os handlers atuais produzem resultados locais auditáveis e não fazem escritas externas nem executam código arbitrário contido nos instrumentos. Consulte `docs/execucao-especializada-instrumentos.md` para contratos e exemplos.


## Análise contextual cumulativa e seleção funcional de tarefas

A execução especializada agora possui uma camada aditiva de análise contextual em `scripts/promptaria_context_router.py` e `scripts/promptaria_contextual_executor.py`. Ela preserva a arquitetura vigente, os três componentes-base e os oito handlers canônicos, sem substituir ou fundir os instrumentos existentes.

Os elementos-base do protocolo-mestre fornecem a estrutura comum; as personalizações de cada demanda fornecem evidências circunstanciais concatenadas — incluindo ações, objeto, finalidade, títulos, IDs, caminhos e campos estruturados. A análise avalia as evidências em conjunto, registra a proveniência dos campos e seleciona cumulativamente todos os handlers sustentados pelo contexto, em vez de encerrar na primeira correspondência. O relatório expõe a cadeia base → personalização → interpretação contextual → seleção de handlers.

O workflow **Promptária — execução especializada** usa o executor contextual e publica três artefatos: plano de préflight, análise contextual e execução especializada. A correspondência por título permanece cumulativa; colisões de identidade continuam sujeitas às regras de desambiguação. A seleção contextual não concede autorização de escrita nem autoriza efeitos externos. Os handlers executam transformações locais determinísticas, e qualquer escrita real permanece sujeita ao executor genérico, às permissões e à confirmação já existentes.

Validação local adicional: `python -m unittest tests.test_promptaria_contextual_executor -v`.


## Protocolo de atualização integral e preservação funcional

O instrumento `instruments/protocolo-operacional-atualizacao-integridade-acervo.md` formaliza a atualização de versões integrais sem perder identidade, rastreabilidade, correferências ou relações entre arquivos. Ele está registrado em `config/instrument-registry.json`, publicado no catálogo `config/instrument-catalog.json` e visível na interface que carrega o registro canônico.

O resolvedor inclui esse protocolo automaticamente nos planos futuros com a identidade `mandatory_update_integrity_preconfiguration`. A inclusão significa recuperação e planejamento, não execução implícita. A política vigente de simulação, autorização explícita, executor separado e validação continua ativa. A automação reconhece títulos e recupera o conteúdo completo dos arquivos Markdown; a verificação final do conteúdo e das operações depende dos testes e evidências de execução correspondentes.

## Instrumento Nocturna: arquitetura da necessidade e identidade sistêmica

O instrumento `instruments/nocturna-arquitetura-necessidade-identidade-sistemica.md` foi adicionado com o título canônico completo, ID `nocturna-arquitetura-necessidade-identidade-sistemica`, nó de interface `instrument:nocturna-arquitetura-necessidade-identidade-sistemica` e referências no registro, catálogo e manifesto de integridade. Seu método cobre inventário de proveniência dos acervos Nocturna, seleção estrutural, reconstrução recursiva, objeções encadeadas, indução fractal como analogia relacional, norma representacional Logos, distinção de estatutos epistêmicos e verificação de não contradição.

O resolvedor inclui o instrumento em planos futuros como `mandatory_nocturna_architecture_preconfiguration`, sem alegar execução nem acesso automático ao repositório externo Nocturna. A análise das coleções e publicações só pode ser declarada concluída quando as fontes estiverem efetivamente acessíveis e verificadas. A inclusão no catálogo não substitui esse acesso nem converte hipóteses em fatos.

## Pré-configuração obrigatória de rastreabilidade para novos instrumentos

O workflow `.github/workflows/promptaria-tests.yml` executa agora `.github/scripts/validate_instrument_traceability.py` em cada pull request e push para `main`. A verificação cruza os arquivos Markdown de `instruments/*.md` com o registro canônico, o catálogo publicado e o manifesto de testes. Uma inclusão ou alteração não pode passar pela validação se faltar uma entrada, houver caminho obsoleto, divergência de título, ID duplicado ou metadados essenciais incompletos.

Para cada instrumento novo, preserve o primeiro cabeçalho Markdown como título canônico e registre no `config/instrument-registry.json`: ID único, caminho, aliases, palavras-chave, funções, relações explícitas no formato `origem->destino`, operações e nó de interface. Atualize também `tests/manifest.json` e regenere `config/instrument-catalog.json` com:

```bash
python scripts/generate_instrument_catalog.py
python .github/scripts/validate_instrument_traceability.py
python -m unittest discover -s tests -v
```

O resolvedor por título continua recuperando todas as ocorrências com normalização de caixa, acentos e pontuação. Títulos canônicos equivalentes não são fundidos nem descartados: representam identidades distintas e exigem desambiguação por ID quando necessário. O gate de rastreabilidade valida referências e metadados; não executa o conteúdo dos instrumentos, não concede permissões de escrita e não transforma uma correspondência lexical em prova de equivalência semântica.



## Ativação funcional explícita e inclusão futura

A existência de um Markdown no repositório, no manifesto ou no catálogo **não ativa** sua correferência funcional. O registro mantém um estado explícito em `activation.enabled`: somente entradas habilitadas podem ser resolvidas pelo título canônico e exibidas no site. O estado inicial preserva ativos apenas `github-operational`, `nocturna-arquitetura-necessidade-identidade-sistemica` e `protocol-update-integrity`; os demais ficam preparados, mas inativos.

Quando um instrumento preparado for efetivamente publicado no site, habilite-o pelo ID já registrado:

```bash
python scripts/activate_instrument.py --id ID-DO-INSTRUMENTO
python scripts/generate_instrument_catalog.py
python .github/scripts/validate_instrument_traceability.py
python -m unittest discover -s tests -v
```

Para um instrumento novo, primeiro crie o Markdown e complete sua entrada no registro com ID único, título idêntico ao primeiro H1, aliases, palavras-chave, funções, relações, operações e nó UI. Inclua-o no manifesto de inventário. Só depois de sua incorporação deliberada ao site execute o ativador. A validação impede que a mera presença de um arquivo amplie o conjunto ativo. A interface e o resolvedor consomem a mesma flag, evitando catálogo visual e correferência funcional divergentes.


## Ativação controlada e pré-configuração futura

A interface e o resolvedor funcional usam exclusivamente os instrumentos com `activation.enabled: true` em `config/instrument-registry.json`. Os três instrumentos-base atualmente habilitados são:

- `github-operational`
- `nocturna-arquitetura-necessidade-identidade-sistemica`
- `protocol-update-integrity`

Os outros instrumentos que já existem permanecem inventariados, mas desativados. Estar em `instruments/`, no manifesto ou no catálogo não basta para habilitar um instrumento existente.

Quando um novo arquivo Markdown é adicionado diretamente a `instruments/` na branch `main`, o workflow `.github/workflows/promptaria-auto-preconfigure.yml` executa primeiro os testes de regressão e, se passarem, chama `.github/scripts/preconfigure_new_instruments.py` para gerar metadados mínimos e sincronizar registro, catálogo e manifesto por meio de um pull request. **O instrumento novo permanece desativado e invisível** (`activation.enabled: false`, `ui.visible: false`, `ui.featured: false`) com estado `prepared_no_executor`. A presença de um título e de um arquivo Markdown não comprova a existência de um executor. A ativação funcional exige revisão e um fluxo explícito posterior, depois que executor, permissões e pré-condições forem verificados. Títulos canônicos duplicados e IDs colidentes bloqueiam o registro automático.

A automação pré-configura identidade e reconhecimento; ela não executa o conteúdo do prompt, não ativa automaticamente o instrumento nem concede permissão de escrita. Para títulos ambíguos, o fluxo falha de forma explícita em vez de escolher silenciosamente um instrumento. O workflow de regressão separado está documentado em `docs/preconfiguration-regression-ci.md`.


## Classificação prévia da demanda: correferência ou automação distinta

Antes de resolver títulos, o workflow executa `scripts/promptaria_route_request.py` e grava `request-routing.json` como artefato auditável. A classificação escolhe uma rota separada:

- `title_coreference`: a demanda cita explicitamente um título de instrumento habilitado em `config/instrument-registry.json`; somente então o resolvedor de títulos é executado.
- `automation_preconfiguration`: a demanda pede criação, ajuste, sincronização ou pré-configuração de automação sem citar um título ativo. O workflow entrega apenas o plano de roteamento e **não** executa a correferência.
- `mixed_coreference_and_automation_preconfiguration`: ambas as intenções aparecem; a resolução de títulos ativos é executada e a intenção de automação fica identificada separadamente.
- `inactive_or_unregistered_reference`: uma referência reconhecida aponta para instrumento desativado; a correferência é bloqueada.
- `unclassified_requires_review`: a intenção não é suficientemente clara; a operação fica pendente de classificação contextual.

O registry é a autoridade para acionamento por título. Os oito instrumentos preexistentes desativados, bem como arquivos que não tenham entrada habilitada no registry, não se tornam acionáveis por aparecerem no catálogo, no diretório ou no texto da demanda. Suas funções de automação distintas continuam preservadas como conteúdo e configuração, mas não são confundidas com correferência por título.

A classificação é conservadora e não executa mutações. Menção de título, presença de arquivo ou geração de plano não equivalem a autorização de escrita. Os testes de roteamento cobrem as rotas de correferência, automação distinta, referência inativa, intenção mista e demanda sem classificação segura.


## Atualização aditiva e autônoma da documentação

O workflow `.github/workflows/promptaria-readme-sync.yml` mantém o README alinhado à árvore real do repositório. Ele é acionado por alterações funcionais na branch `main`, pode ser executado manualmente em **Actions** e realiza uma auditoria semanal de reconciliação. O script `.github/scripts/sync_readme_inventory.py` registra os principais pontos de entrada e gera inventários de instrumentos, scripts, workflows, documentação, testes e configurações.

A seção gerada é delimitada pelos marcadores `PROMPTARIA-README-AUTO:START` e `PROMPTARIA-README-AUTO:END`. O conteúdo editorial existente fora desses marcadores é preservado; apenas a seção gerenciada é regenerada, evitando sobrescrever manualmente o restante do README. A automação faz commit somente quando detecta diferença e usa concorrência controlada para evitar execuções simultâneas.

### Critérios e limites

- A atualização inicial é aditiva: não remove nem reescreve as seções documentais anteriores.
- Mudanças em instrumentos, scripts, testes, documentos, configurações, workflows e arquivos centrais de instrução disparam a sincronização após chegarem à branch `main`.
- A rotina semanal reconcilia o inventário mesmo quando não houve um evento de push elegível.
- O workflow tem permissão de conteúdo para publicar apenas o commit do README; não executa prompts, não altera código funcional e não concede permissões a agentes externos.
- O inventário é evidência estrutural, não substitui revisão semântica humana nem garante que todo comportamento do software esteja descrito com precisão. Novas funcionalidades devem continuar incluindo suas explicações de uso, propósito, limites e validação nas seções editoriais apropriadas.
- A automação depende de GitHub Actions habilitado e de permissões do repositório que permitam ao workflow enviar commits para `main`. Proteções de branch podem exigir ajuste administrativo compatível com a política do projeto.

Para conferir ou disparar a rotina: **Actions → “Promptária - manter README atualizado” → Run workflow**.

<!-- PROMPTARIA-README-AUTO:START -->
## Inventário funcional mantido automaticamente

<!-- Esta seção é regenerada pelo workflow; mantenha conteúdo editorial fora dos marcadores. -->

Esta seção é sincronizada com a árvore versionada do repositório. O inventário comprova presença estrutural, não execução em produção. A auditoria verifica identidade canônica e referências entre índices; não substitui testes comportamentais nem revisão semântica de propósito, entradas, saídas, dependências e limites.

### Arquitetura e pontos de entrada

- Instruções comuns para agentes: AGENTS.md e AI_AGENT_GUIDE.md.
- Instruções de automação: .github/AUTOPILOT.md e .github/copilot-instructions.md.
- Resolução e roteamento: scripts/promptaria_resolver.py, scripts/promptaria_route_request.py e scripts/promptaria_context_router.py.
- Execução e salvaguardas: scripts/promptaria_executor.py, scripts/promptaria_specialized_executor.py e config/promptaria_permissions.json.
- Fonte de identidade: config/instrument-registry.json; catálogo em config/instrument-catalog.json; manifesto em tests/manifest.json.
- Testes Python: python -m unittest discover -s tests -v.
- Testes JavaScript: node --test tests/*.test.mjs.

### Resultado da auditoria estrutural

- Auditoria estrutural e de identidade: PASSOU — H1, registro, catálogo, manifesto, aliases ativos e mapa de execução reconciliados.

### Cobertura semântica documental (indicadores heurísticos)

A lista abaixo compara o conteúdo de cada instrumento com indicadores textuais de propósito, entradas, saídas, dependências, exemplos, limites, permissões e validação. Ela ajuda a localizar lacunas editoriais, mas não comprova que o comportamento descrito está correto; essa confirmação exige leitura e testes específicos.

- **github-operational — Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas** (active): 7/8 indicadores documentais; funções registradas: 13; operações: 14; relações: 34.
  - Revisão editorial sugerida para: exemplos/uso.
- **functional-correference-architecture — ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS: ACIONAMENTO COORDENADO DE INSTRUMENTOS PROMPTUAIS E ARQUITETURA DE ACIONAMENTO, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS, COM CORREFERÊNCIA FUNCIONAL AUTOMÁTICA POR TÍTULOS DOS INSTRUMENTOS PROMPTUAIS, NA QUAL A MENÇÃO GENÉRICA IDENTIFICA O INSTRUMENTO, PRESERVA SUA FUNÇÃO PRÓPRIA E ACIONA SUA EXECUÇÃO, SALVO ATRIBUIÇÃO ESPECÍFICA E INEQUÍVOCA DE FUNÇÃO DIVERSA, COM RECONHECIMENTO MÚTUO, CUMULATIVO, COORDENADO E SIMULTÂNEO DE MÚLTIPLOS TÍTULOS** (prepared_not_published): 7/8 indicadores documentais; funções registradas: 9; operações: 8; relações: 20.
  - Revisão editorial sugerida para: exemplos/uso.
- **coordinator — ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS** (prepared_not_published): 7/8 indicadores documentais; funções registradas: 3; operações: 3; relações: 2.
  - Revisão editorial sugerida para: exemplos/uso.
- **promptaria-instrument-template — MODELO FICTÍCIO — INSTRUMENTO PROMPTUAL DE CORREFERÊNCIA EXTENSIVA** (prepared_not_published): 6/8 indicadores documentais; funções registradas: 4; operações: 7; relações: 7.
  - Revisão editorial sugerida para: exemplos/uso, permissões/segurança.
- **nocturna-arquitetura-necessidade-identidade-sistemica — Nocturna — Arquitetura da Necessidade e Reconstrução Recursiva da Identidade Sistêmica: Princípio, Origem e Fim na Unidade Fractal entre o Explícito e o Implícito, o Físico e o Metafísico, o Universal e o Particular, mediante a Integração Documental, a Correferência Multiescalar, a Indução Causal, a Verificação das Derivações e o Fechamento Arquitetônico da Totalidade — Conservar o Fundamento, Transformar a Função, Reconstruir a Necessidade, Revelar o Todo em Cada Parte e Reconhecer na Origem a Presença Integral de Todas as Consequências Legítimas.** (active): 7/8 indicadores documentais; funções registradas: 7; operações: 8; relações: 9.
  - Revisão editorial sugerida para: exemplos/uso.
- **future-demand-preconfiguration — PRÉ-CONFIGURAÇÃO DE SINCRONIZAÇÃO, CORREFERÊNCIA E VALIDAÇÃO AUTOMÁTICA DA PROMPTÁRIA** (prepared_not_published): 7/8 indicadores documentais; funções registradas: 3; operações: 3; relações: 2.
  - Revisão editorial sugerida para: exemplos/uso.
- **catalog-sitemap-preconfiguration — PRÉCONFIGURAÇÃO DE SINCRONIZAÇÃO, CORREFERÊNCIA E VALIDAÇÃO AUTOMÁTICA DA PROMPTÁRIA** (prepared_not_published): 7/8 indicadores documentais; funções registradas: 3; operações: 3; relações: 2.
  - Revisão editorial sugerida para: exemplos/uso.
- **master-activation — PROTOCOLO-MESTRE DE ACIONAMENTO DE INSTRUMENTOS PROMPTUAIS PRONTO PARA EXECUÇÃO** (prepared_not_published): 7/8 indicadores documentais; funções registradas: 3; operações: 3; relações: 7.
  - Revisão editorial sugerida para: dependências.
- **master-execution — Protocolo-mestre de execução correta desde a primeira solicitação** (prepared_not_published): 7/8 indicadores documentais; funções registradas: 3; operações: 3; relações: 2.
  - Revisão editorial sugerida para: exemplos/uso.
- **protocol-update-integrity — PROTOCOLO OPERACIONAL DE ATUALIZAÇÃO, REINTEGRAÇÃO E PRESERVAÇÃO FUNCIONAL DO ACERVO DE INSTRUMENTOS PROMPTUAIS DO PROMPTÁRIA** (active): 6/8 indicadores documentais; funções registradas: 4; operações: 6; relações: 5.
  - Revisão editorial sugerida para: saídas/resultados, exemplos/uso.

### Inventário versionado

#### Instrumentos promptuais (10)

- instruments/acione-a-promptaria-pelo-github.md
- instruments/arquitetura-unificada-acionamento-correferencia-recuperacao-aplicacao.md
- instruments/arquitetura-unificada.md
- instruments/modelo-instrumento-promptual-correferencia.md
- instruments/nocturna-arquitetura-necessidade-identidade-sistemica.md
- instruments/preconfiguracao-correspondencia-futura-e-cadeia.md
- instruments/preconfiguracao-sincronizacao-catalogo-sitemap.md
- instruments/protocolo-mestre-acionamento-automatico.md
- instruments/protocolo-mestre-execucao-correta.md
- instruments/protocolo-operacional-atualizacao-integridade-acervo.md

#### Scripts operacionais (18)

- scripts/activate_instrument.py
- scripts/generate_instrument_catalog.py
- scripts/promptaria_audit_anchor.py
- scripts/promptaria_context_router.py
- scripts/promptaria_contextual_executor.py
- scripts/promptaria_execute_preconfigured.py
- scripts/promptaria_executor.py
- scripts/promptaria_operation_guard.py
- scripts/promptaria_operational_audit.py
- scripts/promptaria_preflight.py
- scripts/promptaria_prepare_executor_request.py
- scripts/promptaria_registry_audit.py
- scripts/promptaria_resolver.py
- scripts/promptaria_route_request.py
- scripts/promptaria_specialized_executor.py
- scripts/promptaria_validate_result.py
- scripts/validate_instrument_reference_contract.py
- scripts/validate_instrument_registry.py

#### Workflows do GitHub Actions (17)

- .github/workflows/promptaria-auto-merge.yml
- .github/workflows/promptaria-auto-preconfigure.yml
- .github/workflows/promptaria-correfencia.yml
- .github/workflows/promptaria-instrument-registry.yml
- .github/workflows/promptaria-integracao-pr.yml
- .github/workflows/promptaria-operation-guard.yml
- .github/workflows/promptaria-pages.yml
- .github/workflows/promptaria-pr-checks.yml
- .github/workflows/promptaria-preconfig-validation.yml
- .github/workflows/promptaria-preflight.yml
- .github/workflows/promptaria-readme-sync.yml
- .github/workflows/promptaria-registry-audit.yml
- .github/workflows/promptaria-resolvedor-js.yml
- .github/workflows/promptaria-specialized-execution.yml
- .github/workflows/promptaria-tests.yml
- .github/workflows/remove-interface-text.yml
- .github/workflows/testes-resolvedor.yml

#### Documentação (9)

- docs/analise-contextual-evidencias.md
- docs/auditoria-operacional-inicial.md
- docs/auditoria-operacional-reproduzivel.md
- docs/execucao-especializada-instrumentos.md
- docs/integridade-sistemica-e-rastreabilidade-interface.md
- docs/legacy/arquitetura-unificada-correferencia-funcional-automatica.md
- docs/matriz-instrumento-executor.md
- docs/preconfiguracao-protocolo-mestre-e-correferencia.md
- docs/registry-disambiguation.md

#### Testes automatizados (28)

- tests/test_correfencia_execution_bundle.py
- tests/test_correfencia_funcional.md
- tests/test_instrument_catalog.py
- tests/test_instrument_reference_contract.py
- tests/test_interface_traceability.py
- tests/test_preconfigure_new_instruments.py
- tests/test_promptaria_audit_report.py
- tests/test_promptaria_contextual_executor.py
- tests/test_promptaria_corref.py
- tests/test_promptaria_execute_preconfigured.py
- tests/test_promptaria_execution_map.py
- tests/test_promptaria_executor.py
- tests/test_promptaria_functional_preconfiguration.py
- tests/test_promptaria_operational_audit.py
- tests/test_promptaria_preflight.py
- tests/test_promptaria_prepare_executor_request.py
- tests/test_promptaria_registry_audit.py
- tests/test_promptaria_repository_integrity.py
- tests/test_promptaria_resolver.py
- tests/test_promptaria_route_request.py
- tests/test_promptaria_specialized_executor.py
- tests/test_promptaria_validate_result.py
- tests/test_promptaria_workflow_integrity.py
- tests/test_resolver_contract.py
- tests/test_traceability_context_router.py
- tests/test_traceability_preconfiguration.py
- tests/teste-cadeia-navegacional.mjs
- tests/teste-registro-instrumentos.py

#### Configurações JSON (10)

- config/instrument-catalog.json
- config/instrument-execution-map.json
- config/instrument-reference-contract.json
- config/instrument-registry.json
- config/interface-traceability-current.json
- config/interface-traceability.json
- config/promptaria_permissions.json
- config/segment-integration-policy.json
- config/traceability-graph-current.json
- config/traceability-graph.json

<!-- PROMPTARIA-README-AUTO:END -->

## Workflow de pré-configuração do protocolo-mestre

O workflow `.github/workflows/promptaria-protocolo-mestre.yml` permite iniciar manualmente uma pré-configuração por **Actions → Promptária — protocolo-mestre e pré-configuração funcional → Run workflow**.

Entradas:
- `request` (obrigatória): a demanda concreta a processar.
- `instrument_titles` (opcional): títulos adicionais, um por linha; todos são encaminhados ao resolvedor.
- `destination` (opcional): destino proposto para constar no plano. Informar um destino não concede autorização de escrita.

O workflow constrói um payload estruturado, executa `scripts/promptaria_preflight.py`, resolve títulos com `scripts/promptaria_resolver.py`, valida o resultado com `scripts/promptaria_validate_result.py` e publica os arquivos de evidência como artefato do GitHub Actions por 30 dias.

### Limites e validação

Este workflow opera em modo de planejamento (`plan_only`, `dry_run: true`) e usa permissões de conteúdo somente para leitura. Não escreve automaticamente no repositório nem em Nocturna. Uma correspondência encontrada não prova que o conteúdo foi recuperado, aplicado ou executado; cada estado exige evidência própria. Escritas reais dependem de um executor separado, destino permitido, permissões e confirmação explícita.

Para executar, abra o workflow na aba **Actions**, escolha **Run workflow**, preencha a demanda e, se necessário, os títulos adicionais, e inicie a execução. Consulte o resumo e baixe o artefato para revisar o plano e a rastreabilidade. O workflow deve ser testado antes de ser considerado operacionalmente aprovado.

## Integração automática de pull requests

O workflow `.github/workflows/promptaria-auto-merge.yml` reduz etapas manuais de integração. Quando `Promptária PR Checks` termina com sucesso para uma pull request, a automação pode mesclá-la em `main` sem exigir a caixa de seleção de opt-in no texto da PR nem o comentário manual `/promptaria merge`.

A automação só considera pull requests abertas, não marcadas como rascunho, originadas no próprio repositório e destinadas a `main`. Ela confirma que o commit atual corresponde exatamente à revisão testada e repete a conferência imediatamente antes do merge. Se o HEAD mudar, se os checks falharem ou se a PR não cumprir os critérios, a integração automática não ocorre.

A mesclagem usa squash e continua sujeita às regras de proteção e às verificações obrigatórias configuradas no GitHub. Esta automação elimina passos manuais redundantes; não remove testes, aprovações obrigatórias nem outras políticas de proteção. O tempo de execução dos próprios testes permanece dependente dos workflows e dos runners.


## Fluxo de integração simplificado na main

O fluxo padrão de pull requests é **branch → PR → checks automáticos → merge squash**. O workflow `.github/workflows/promptaria-pr-checks.yml` valida sintaxe Python/JSON, rastreabilidade dos instrumentos, testes de regressão e o smoke test funcional. Checks antigos da mesma PR são cancelados quando chega uma nova revisão, evitando gastar runners em commits obsoletos.

O workflow `.github/workflows/promptaria-auto-merge.yml` pode mesclar automaticamente PRs próprias, abertas, não marcadas como rascunho e destinadas a `main`, depois que `Promptária PR Checks` termina com sucesso. O SHA é conferido contra a revisão testada e novamente antes do merge. O comentário opcional `/promptaria merge` apenas prepara uma PR em rascunho; não contorna os checks.

A automação não apaga dados nem desativa auditoria, revisões obrigatórias, checks obrigatórios ou proteções de branch. Essas políticas administrativas continuam prevalecendo. Antes de adicionar novos checklists ou workflows, reutilize os existentes quando a cobertura for equivalente. Consulte `.github/PR_AUTOMATION_POLICY.md` e `.github/AUTOPILOT.md` para a regra operacional persistente.


## Fluxo de integração simplificado na main

O fluxo padrão de pull requests é **branch → PR → checks automáticos → merge squash**. O workflow `.github/workflows/promptaria-pr-checks.yml` valida sintaxe Python/JSON, rastreabilidade dos instrumentos, testes de regressão e o smoke test funcional. Checks antigos da mesma PR são cancelados quando chega uma nova revisão, evitando gastar runners em commits obsoletos.

O workflow `.github/workflows/promptaria-auto-merge.yml` pode mesclar automaticamente PRs próprias, abertas, não marcadas como rascunho e destinadas a `main`, depois que `Promptária PR Checks` termina com sucesso. O SHA é conferido contra a revisão testada e novamente antes do merge. O comentário opcional `/promptaria merge` apenas prepara uma PR em rascunho; não contorna os checks.

A automação não apaga dados nem desativa auditoria, revisões obrigatórias, checks obrigatórios ou proteções de branch. Essas políticas administrativas continuam prevalecendo. Antes de adicionar novos checklists ou workflows, reutilize os existentes quando a cobertura for equivalente. Consulte `.github/PR_AUTOMATION_POLICY.md` e `.github/AUTOPILOT.md` para a regra operacional persistente.
