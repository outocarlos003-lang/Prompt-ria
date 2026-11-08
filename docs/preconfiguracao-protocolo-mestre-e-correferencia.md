# Pré-configuração funcional: protocolo-mestre, autorização delimitada e correferência

## Objetivo

Preparar um plano determinístico para cada demanda, identificando instrumentos por título canônico, alias, ID ou caminho, preservando referências múltiplas e registrando as condições de autorização antes de qualquer efeito colateral.

## Comportamento

Execute `scripts/promptaria_preflight.py` com um pedido JSON:

```sh
python scripts/promptaria_preflight.py \
  --request request.json \
  --output artifacts/promptaria-plan.json
```

O JSON de entrada usa `request` como texto da demanda e pode incluir `destination`. O plano inclui todos os instrumentos encontrados, evidências da correspondência, colisões, status de pré-autorização e declaração explícita de que nenhuma operação foi executada.

## Regra de pré-autorização

A presença conjunta de um protocolo-mestre e de pelo menos um instrumento inequivocamente identificado pode participar da pré-autorização **somente** quando a solicitação também contém intenção explícita de escrita e um destino relativo dentro de `artifacts/`. Uma menção isolada não é autorização. Colisões de identidade, caminhos fora do escopo e operações sem destino válido bloqueiam a pré-autorização.

A pré-autorização é deliberadamente estreita: não inclui `instruments/`, configuração, workflows, código, arquivos externos, operações destrutivas ou serviços externos. Uma escrita real pode usar `scripts/promptaria_execute_preconfigured.py` com o plano gerado e o pedido de escrita. Esse wrapper recalcula a elegibilidade a partir do manifesto e do mapa canônicos e exige que demanda e destino coincidam com o plano. A execução ainda exige `dry_run=false`, permissões do executor e `--confirm-operation` com o `operation_id` exato. Isso permite presumir autorização apenas para a escrita estreita previamente elegível, sem transformar a simples presença de um título em permissão irrestrita.

Exemplo de execução local, após gerar e revisar o plano:

```sh
python scripts/promptaria_execute_preconfigured.py \
  --request executor-request.json \
  --preflight artifacts/promptaria-plan.json \
  --confirm-operation preflight-write-001
```

O workflow `.github/workflows/promptaria-preflight.yml` disponibiliza o planejamento via `workflow_dispatch` e publica o JSON como artefato. Ele não executa escritas reais automaticamente.

## Correferência funcional

- Normaliza maiúsculas/minúsculas, acentos, pontuação e hífens.
- Reconhece títulos, aliases, IDs e caminhos do manifesto.
- Preserva referências a múltiplos instrumentos na mesma demanda.
- Não escolhe arbitrariamente entre títulos canônicos que colidem após normalização; requer ID ou caminho explícito.
- Não declara execução especializada quando o mapa não registra um executor especializado.
- Emite um plano reproduzível em JSON para validação, auditoria e integração a workflows.

## Limites atuais

Este preflight é uma etapa funcional de resolução e planejamento, não um daemon nem um gatilho automático sobre conversas futuras do ChatGPT. Para acionamento em GitHub Actions, o workflow deve chamar o script com um payload de demanda e publicar/arquivar o plano. A integração não deve converter comentários não confiáveis em execução de escrita sem validação e confirmação específicas.


## Interconexão canônica do instrumento fixo

O protocolo-mestre, a pré-configuração padrão e a automação de correspondência por título devem referenciar a mesma unidade operacional, sem fundir as identidades documentais desses segmentos:

- ID: `github-operational`.
- Nó: `instrument:github-operational`.
- Registro autoritativo: `config/instrument-registry.json`.
- Fonte integral: `instruments/acione-a-promptaria-pelo-github.md`.
- Funções reunidas: recuperação e verificação da fonte, resolução por título/alias/ID/caminho conforme as regras canônicas, preservação do envelope estruturado, encaminhamento ao protocolo-mestre e emissão de evidências de rastreabilidade.
- A pré-configuração inclui o instrumento fixo no plano como componente-base; a automação por título continua resolvendo os demais instrumentos cumulativamente, sem parar na primeira correspondência.
- Os segmentos conservam seus próprios IDs, títulos, caminhos e funções. A relação é explícita e navegável, não uma duplicação de identidade.
- O estado padrão continua sendo planejamento/simulação; autorização de escrita, execução especializada, validação, publicação e inspeção de interface são estados distintos.

## Interconexão funcional bidirecional e contrato de preservação

Esta pré-configuração usa a mesma identidade operacional referenciada pelo protocolo-mestre e pela automação de correspondência por título. O nó é compartilhado; os segmentos e suas funções continuam distintos.

- **ID canônico do instrumento operacional:** `github-operational`.
- **Nó:** `instrument:github-operational`.
- **Registro autoritativo:** `config/instrument-registry.json`.
- **Fonte integral:** `instruments/acione-a-promptaria-pelo-github.md`.
- **Automação de correspondência por título:** `functional-correference-architecture`, arquivo `instruments/arquitetura-unificada-correferencia-funcional-automatica.md`.
- **Protocolo-mestre:** `master-activation`, arquivo `instruments/protocolo-mestre-acionamento-automatico.md`.

### Papéis complementares

1. **Correspondência por título:** identifica instrumentos por título canônico normalizado para comparação, conserva a proveniência e resolve cumulativamente todas as correspondências pertinentes, bloqueando ambiguidades.
2. **Protocolo-mestre:** coordena os componentes-base e os instrumentos especializados, integra a demanda contextual e aplica os critérios de satisfação verificável.
3. **Pré-configuração padrão:** preserva o contexto estruturado, os parâmetros, a origem, os destinos propostos, a autorização, as dependências e os estados da operação; não transforma fotografias históricas em estado atual.
4. **Instrumento operacional `github-operational`:** inspeciona o repositório, localiza e recupera conteúdo integral, normaliza e preserva o envelope da demanda, mantém metadados e aliases, encaminha operações autorizadas e registra evidências de rastreabilidade.

Esses papéis são aditivos. Nenhum substitui, absorve ou reduz as funções dos demais. O mesmo instrumento não deve receber IDs, caminhos ou nós paralelos só porque aparece em mais de um segmento.

### Relações e validação

As relações canônicas incluem `master-protocol-fixed-instrument->github-operational`, `master-preconfiguration->github-operational`, `functional-correference-architecture->github-operational`, `github-operational->functional-correference-architecture`, `title-correspondence-automation->instrument:github-operational`, `instrument:github-operational->title-correspondence-automation`, `standard-preconfiguration->instrument:github-operational` e `instrument:github-operational->standard-preconfiguration`.

A validação pós-alteração deve confirmar que `config/instrument-registry.json`, `config/instrument-catalog.json` e `tests/manifest.json` mantêm o mesmo ID e caminho canônicos e aliases sincronizados; que o nó continua `instrument:github-operational`; e que a ativação e os estados de execução não foram alterados implicitamente. A inclusão no plano continua diferente de autorização, tentativa, execução confirmada e resultado validado.

## Interconexão canônica com a arquitetura unificada

A pré-configuração padrão reconhece a arquitetura unificada como unidade documental própria, sem confundi-la com o instrumento operacional fixo nem com o protocolo-mestre.

- **Arquitetura unificada/correspondência por título:** ID `functional-correference-architecture`, nó `instrument:functional-correference-architecture`, fonte `instruments/arquitetura-unificada-correferencia-funcional-automatica.md`.
- **Protocolo-mestre:** ID `master-activation`, nó `instrument:master-activation`, fonte `instruments/protocolo-mestre-acionamento-automatico.md`.
- **Instrumento fixo:** ID `github-operational`, nó `instrument:github-operational`, fonte `instruments/acione-a-promptaria-pelo-github.md`.
- **Registro autoritativo:** `config/instrument-registry.json`.
- **Catálogo sincronizado:** `config/instrument-catalog.json`.
- **Manifesto de testes:** `tests/manifest.json`.

A arquitetura unificada coordena a identificação e a aplicação cumulativa dos instrumentos; a correspondência por título resolve as referências; o protocolo-mestre organiza dependências e satisfação da demanda; o instrumento fixo recupera conteúdo e mantém o envelope operacional; a pré-configuração preserva contexto, parâmetros, origem, destino, autorização e estados. Esses papéis são complementares, não intercambiáveis.

Relações canônicas incluem `functional-correference-architecture->master-activation`, `master-activation->functional-correference-architecture`, `functional-correference-architecture->github-operational`, `github-operational->functional-correference-architecture`, `master-preconfiguration->github-operational` e `standard-preconfiguration->functional-correference-architecture`.

A presença no registro ou no plano não concede autorização irrestrita nem comprova execução. Permanecem distintos planejamento, autorização, tentativa, execução confirmada e resultado validado. Qualquer divergência entre registro, catálogo, manifesto, IDs, caminhos ou nós deverá ser tratada como falha de integridade.

## Política de integração dos três segmentos protegidos

A partir desta atualização, a pré-configuração trata **Protocolo-mestre**, **Pré-configuração padrão** e **Automação de correferência por título** como segmentos protegidos contra expansão automática de instrumentos.

Os únicos instrumentos integrados automaticamente nesses três segmentos são:

1. `github-operational` — **Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas**;
2. `functional-correference-architecture` — **ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS: ... COM RECONHECIMENTO MÚTUO, CUMULATIVO, COORDENADO E SIMULTÂNEO DE MÚLTIPLOS TÍTULOS**.

Isso **não** impede que qualquer outro instrumento promptual habilitado seja localizado, recuperado, acionado e executado segundo seu próprio conteúdo e sua capacidade registrada. Seleção/acionamento e integração nos três segmentos são estados diferentes.

A regra automática é **fechada por padrão**: a mera existência no catálogo, habilitação, menção por título, correspondência contextual ou seleção de um instrumento não o insere nos três segmentos. Uma integração adicional somente pode ocorrer quando a demanda fornecer `segment_integration_need` com a referência do instrumento e uma justificativa concreta da necessidade para a demanda atual, ou `segment_integration_request` com pedido explícito de integração. O resolvedor registra a evidência e mantém os demais instrumentos independentes quando a exceção não estiver presente.

A implementação executável dessa política está em `config/segment-integration-policy.json` e `scripts/promptaria_context_router.py`. O resultado do roteamento expõe separadamente `selected_instrument_ids` e `segment_integration`, incluindo `blocked_automatic_integrations`, para impedir que a ativação de um instrumento seja confundida com sua incorporação estrutural.

## Fonte integral canônica da arquitetura

A fonte integral da arquitetura coordenadora está em [arquitetura-unificada-acionamento-correferencia-recuperacao-aplicacao.md](../instruments/arquitetura-unificada-acionamento-correferencia-recuperacao-aplicacao.md). A pré-configuração continua sendo documento complementar, com função própria e distinta.
