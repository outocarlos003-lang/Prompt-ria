# PROTOCOLO-MESTRE DE ACIONAMENTO DE INSTRUMENTOS PROMPTUAIS PRONTO PARA EXECUÇÃO

## TÍTULO COORDENADOR/OPERACIONAL INTEGRAL

ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS: ACIONAMENTO COORDENADO DE INSTRUMENTOS PROMPTUAIS E ARQUITETURA DE ACIONAMENTO, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS, COM CORREFERÊNCIA FUNCIONAL AUTOMÁTICA POR TÍTULOS DOS INSTRUMENTOS PROMPTUAIS, NA QUAL A MENÇÃO GENÉRICA IDENTIFICA O INSTRUMENTO, PRESERVA SUA FUNÇÃO PRÓPRIA E ACIONA SUA EXECUÇÃO, SALVO ATRIBUIÇÃO ESPECÍFICA E INEQUÍVOCA DE FUNÇÃO DIVERSA, COM RECONHECIMENTO MÚTUO, CUMULATIVO, COORDENADO E SIMULTÂNEO DE MÚLTIPLOS TÍTULOS

## DIRETRIZ GERAL:

Reconheça, recupere, coordene e aplique os instrumentos promptuais por seus títulos, preservando suas funções próprias e articulando-as, cumulativa e simultaneamente, à demanda específica, até sua satisfação verificável.

## 1. INSTRUMENTO COORDENADOR/OPERACIONAL FIXO:

ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS: ACIONAMENTO COORDENADO DE INSTRUMENTOS PROMPTUAIS E ARQUITETURA DE ACIONAMENTO, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS, COM CORREFERÊNCIA FUNCIONAL AUTOMÁTICA POR TÍTULOS DOS INSTRUMENTOS PROMPTUAIS, NA QUAL A MENÇÃO GENÉRICA IDENTIFICA O INSTRUMENTO, PRESERVA SUA FUNÇÃO PRÓPRIA E ACIONA SUA EXECUÇÃO, SALVO ATRIBUIÇÃO ESPECÍFICA E INEQUÍVOCA DE FUNÇÃO DIVERSA, COM RECONHECIMENTO MÚTUO, CUMULATIVO, COORDENADO E SIMULTÂNEO DE MÚLTIPLOS TÍTULOS

## 2. INSTRUMENTO OPERACIONAL FIXO:

ACIONE A PROMPTÁRIA PELO GITHUB PARA INSERIR, RECUPERAR E APLICAR DEMANDAS

**Identidade canônica do instrumento fixo:** `id=github-operational`; `ui.node_id=instrument:github-operational`; registro autoritativo `config/instrument-registry.json`; fonte `instruments/acione-a-promptaria-pelo-github.md`. Este vínculo não cria uma segunda identidade.

## 3. QUAIS OUTROS INSTRUMENTOS PROMPTUAIS DEVEM SER ACIONADOS? [É OPCIONAL]

INSIRA AQUI, SE HOUVER:

## 4. QUAL É A DEMANDA ESPECÍFICA, SUA FINALIDADE E O RESULTADO ESPERADO?

INSIRA A DEMANDA A SEGUIR:

---

## Regra operacional de préconfiguração

Este protocolo é o modelo genérico padrão para novas demandas transmitidas à Promptária. O coordenador e o instrumento operacional fixo devem ser incluídos automaticamente no plano de resolução, mesmo quando seus títulos não forem repetidos na demanda. Além deles, cada instrumento cujo título canônico seja mencionado deve ser identificado e recuperado, preservando-se todas as correspondências; não se deve interromper a busca na primeira ocorrência nem impor limite arbitrário de instrumentos.

A menção genérica a um título existente preserva e aciona a função própria desse instrumento. Só uma atribuição específica e inequívoca autoriza tratá-lo com função diversa. A correspondência lexical automatizada identifica títulos, mas não deve fingir compreender uma exceção semântica: exceções ambíguas ficam sinalizadas para revisão contextual.

A execução só pode ser declarada quando houver evidência técnica correspondente. Identificação, recuperação do conteúdo, inclusão no plano, tentativa de execução, execução confirmada e resultado validado são estados distintos. A demanda deve ser enviada por um evento GitHub autorizado; este arquivo não concede acesso automático a conversas do ChatGPT nem substitui permissões externas.

## Critério de satisfação verificável

Antes de concluir, conferir: (a) os dois instrumentos fixos; (b) todos os títulos adicionais reconhecidos; (c) conteúdo recuperado de cada unidade; (d) preservação das funções próprias; (e) exceções e conflitos; (f) finalidade e resultado esperado; (g) origem, destino e autorização, quando houver escrita; e (h) evidências que sustentem qualquer alegação de execução ou conclusão.


## Préconfiguração estruturada de demandas e correspondência futura (schema 2.3)

Quando uma solicitação contiver um objeto JSON estruturado como o modelo de operação schema_version 2.3, tratar o objeto como contexto operacional estruturado, não como texto descartável. Preservar integralmente o objeto recebido e seus campos; extrair para correspondência apenas os campos textuais e listas relevantes, sem reescrever, apagar ou inferir como atuais os dados históricos.

A resolução pré-configurada deve:
1. reconhecer operação, demanda, origem, autorização, transformação, destinos, validação, cadeia de produção, invariantes navegacionais e estado;
2. correlacionar todos os títulos de instrumentos mencionados com os títulos canônicos dos arquivos em `instruments/`, aplicando normalização Unicode, caixa e pontuação, conservando todas as correspondências;
3. incluir sempre os três componentes-base definidos pelo resolvedor, além dos instrumentos especializados identificados;
4. manter separados os estados histórico, pretendido, planejado, tentado, executado e validado;
5. tratar os campos `validation`, `catalog_paths`, `catalog_count`, `status` e `audit_after_removal.current_state` como fotografias temporais quando o próprio objeto os qualificar como históricos; confirmar o estado ativo lendo o repositório antes de mutações;
6. usar `source.catalog_source` como fonte declarada de verdade apenas depois de confirmar que o caminho existe na estrutura real. Não presumir que a estrutura Promptária/manifest.json descrita em exemplos exista neste repositório;
7. considerar todos os destinos propostos, mas não criar, remover, renomear ou sobrescrever arquivos apenas porque aparecem no JSON. Exigir revisão de conflitos, autorização explícita aplicável e validação dos caminhos;
8. preservar conteúdo operacional integral e identidade individual de cada instrumento; não converter conteúdo em resumo, artigo ou fusão;
9. conferir links, referências anterior/próximo, entradas de índice, sitemap, README e rastreabilidade quando esses artefatos existirem na arquitetura real;
10. executar testes de regressão e validação pós-gravação, relatando separadamente verificações aprovadas, falhas e etapas não executadas.

Para solicitações estruturadas, o resolvedor deve expor no resultado um `operation_context` que preserve os campos operacionais reconhecidos e assinale que a mutação ainda exige revisão. A préconfiguração melhora a correspondência desde a primeira solicitação, mas não concede permissão de escrita, não transforma planos em execução e não substitui validação semântica humana. O modo seguro padrão continua sendo simulação.


## Análise contextual cumulativa por evidências circunstanciais concatenadas

Os três componentes-base deste protocolo — arquitetura coordenadora, protocolo-mestre e instrumento operacional do GitHub — constituem o quadro fixo de interpretação, não uma tarefa genérica que substitui a demanda concreta. Em cada ocasião, as personalizações fornecidas pelo solicitante e o contexto disponível acrescentam evidências circunstanciais concatenadas sobre a operação pertinente: ação solicitada, finalidade, objeto, instrumentos mencionados, campos estruturados, origem, destino, transformação, dependências, validação, restrições e resultado esperado.

A análise deve considerar conjuntamente o quadro-base e essas personalizações para determinar quais tarefas específicas correspondem à ocasião. Deve registrar a proveniência das evidências, correlacionar cada conclusão com os sinais observados e preservar todas as tarefas sustentadas pelo contexto, sem interromper o processamento na primeira correspondência. A seleção cumulativa não autoriza fundir instrumentos distintos nem altera suas funções próprias.

A correferência funcional automática por título atua em conjunto com a análise contextual: títulos canônicos, IDs e caminhos identificam instrumentos; o contexto determina a pertinência funcional e a ordem de aplicação, respeitando dependências, validações e colisões de identidade. Uma colisão de título continua bloqueada até desambiguação explícita. Uma atribuição de função diversa continua exigindo especificidade e inequívoco sentido; quando a evidência contextual não basta, registrar a incerteza em vez de inventar intenção.

A automação deve executar o handler especializado correspondente quando a identidade estiver resolvida, a capacidade estiver implementada e as condições de validação forem satisfeitas. Deve emitir a cadeia auditável base → personalização → interpretação contextual → seleção da tarefa → execução do handler → validação do resultado. Identificação, planejamento, execução local do handler, gravação no repositório, publicação e efeitos externos continuam sendo estados diferentes.

Esta regra é aditiva: preserva os quatro elementos estruturais do modelo genérico, os três componentes-base, os instrumentos canônicos, a política de correspondência cumulativa, as regras de segurança, os estados de execução e os critérios de satisfação verificável já definidos neste arquivo. Não concede autorização implícita para escrita, exclusão, publicação, deploy ou chamada externa. Os controles vigentes de simulação, permissões mínimas, validação de destino, executor separado, auditoria e confirmação explícita permanecem obrigatórios.


## Interconexão do protocolo-mestre com a correspondência por título e a pré-configuração padrão

O instrumento operacional fixo acima é a mesma unidade canônica referida pela automação de correspondência por título e pela pré-configuração padrão. A identidade não é inferida pelo nome do segmento: é resolvida pelo registro `config/instrument-registry.json`, ID `github-operational` e nó `instrument:github-operational`.

- O protocolo-mestre referencia `master-protocol-fixed-instrument->github-operational`.
- A automação de correspondência por título referencia `functional-correference-architecture->github-operational`.
- A pré-configuração padrão referencia `master-preconfiguration->github-operational`.
- O instrumento fixo cumpre cumulativamente recuperação da fonte integral, normalização e preservação do envelope estruturado, encaminhamento por título canônico, manutenção dos aliases e emissão de evidências de integridade e rastreabilidade.
- O ID, o caminho e o nó permanecem estáveis; as identidades documentais dos segmentos coordenadores continuam distintas.
- O reconhecimento e a inclusão no plano não equivalem à execução de escrita. Mantêm-se as regras de autorização, validação, simulação e evidência já definidas neste protocolo.

## Interconexão operacional obrigatória: protocolo-mestre, correspondência por título e instrumento fixo

O instrumento fixo citado neste protocolo é a mesma unidade identificada no registro central. Resolver sua identidade pelo ID e nó, não por semelhança textual nem por cópia local.

- **ID canônico:** `github-operational`.
- **Nó compartilhado:** `instrument:github-operational`.
- **Registro autoritativo:** `config/instrument-registry.json`.
- **Fonte integral:** `instruments/acione-a-promptaria-pelo-github.md`.
- **Automação de correspondência por título:** `instruments/arquitetura-unificada-correferencia-funcional-automatica.md`, identidade documental `functional-correference-architecture`.
- **Pré-configuração e documentação de autorização:** `docs/preconfiguracao-protocolo-mestre-e-correferencia.md`.

### Contrato de interconexão e preservação funcional

1. O protocolo-mestre mantém a coordenação, a composição dos componentes-base, a análise contextual cumulativa, as prioridades, as dependências e os critérios de satisfação verificável.
2. A automação de correspondência por título mantém a identificação por título canônico, normalização controlada, resolução cumulativa de múltiplos instrumentos, proveniência e bloqueio de ambiguidades.
3. O instrumento `github-operational` mantém as funções operacionais próprias: inspeção do repositório, localização e recuperação integral de recursos, estruturação e preservação do envelope da demanda, normalização de entrada, correlação de aliases/IDs/caminhos, encaminhamento de operações autorizadas e rastreabilidade das evidências.
4. A pré-configuração padrão preserva os campos estruturados, os destinos, a autorização, as dependências, os estados históricos e atuais e a validação. Não converte dados históricos em estado atual nem plano em execução.
5. A interconexão é bidirecional e explícita: `master-protocol-fixed-instrument->github-operational`, `master-preconfiguration->github-operational`, `title-correspondence-automation->instrument:github-operational`, `instrument:github-operational->title-correspondence-automation`, `instrument:github-operational->instrument:master-activation` e `instrument:github-operational->instrument:functional-correference-architecture`.
6. O ID, o caminho e o nó operacional permanecem únicos. As identidades documentais e os papéis do protocolo-mestre e da automação permanecem separados; nenhuma função preexistente é removida ou absorvida.
7. A inclusão automática no plano não é autorização de escrita. Permanecem obrigatórios o executor separado, o destino permitido, a autorização explícita aplicável, a validação de caminho e a evidência técnica para cada estado declarado.

A cadeia de rastreio entre segmentos deve permitir percorrer nos dois sentidos: segmento → relação registrada → ID canônico → nó → arquivo-fonte e arquivo-fonte → nó → segmentos relacionados. Qualquer vínculo ausente, colisão de identidade ou divergência entre registro, catálogo e manifesto deve ser relatado como falha de integridade, sem sucesso presumido.
## Interconexão canônica com a arquitetura unificada de acionamento e correferência

O protocolo-mestre mantém sua identidade documental `master-activation` e seu papel próprio de coordenação. A arquitetura unificada é uma unidade distinta, identificada pelo título integral e registrada como `functional-correference-architecture`; sua relação com o protocolo-mestre não constitui fusão nem substituição de funções.

- **Protocolo-mestre:** ID `master-activation`, nó `instrument:master-activation`, fonte `instruments/protocolo-mestre-acionamento-automatico.md`.
- **Arquitetura unificada/correspondência por título:** ID `functional-correference-architecture`, nó `instrument:functional-correference-architecture`, fonte `instruments/arquitetura-unificada-correferencia-funcional-automatica.md`.
- **Instrumento operacional fixo:** ID `github-operational`, nó `instrument:github-operational`, fonte `instruments/acione-a-promptaria-pelo-github.md`.
- **Registro canônico:** `config/instrument-registry.json`.
- **Pré-configuração padrão:** `docs/preconfiguracao-protocolo-mestre-e-correferencia.md`.

### Contrato intersegmentos

1. O protocolo-mestre coordena a demanda, os componentes-base, as dependências, a ordem operacional e a verificação da satisfação.
2. A arquitetura unificada identifica e articula instrumentos por seus títulos, preserva a função própria de cada unidade, resolve múltiplas correspondências cumulativamente e organiza recuperação, contextualização, parametrização, adaptação e validação.
3. O instrumento fixo `github-operational` mantém sua função operacional de recuperação, normalização da entrada, preservação do envelope, resolução de aliases/IDs/caminhos e rastreabilidade.
4. A pré-configuração padrão conserva os parâmetros e estados da operação e não converte um plano em execução nem uma referência em autorização.
5. As relações são registradas no catálogo autoritativo por IDs e nós canônicos. Não se criam cópias do instrumento fixo nem se reutiliza seu ID para a arquitetura coordenadora.
6. A inclusão ou identificação de um instrumento não equivale a autorização de escrita. Permanecem vigentes as restrições de permissões, destino, confirmação, validação e evidência técnica.

Relações a conservar nos dois sentidos quando aplicáveis: `master-activation->functional-correference-architecture`, `functional-correference-architecture->master-activation`, `functional-correference-architecture->github-operational`, `github-operational->functional-correference-architecture`, `master-protocol-fixed-instrument->github-operational` e `master-preconfiguration->github-operational`.

A validação deverá verificar a consistência entre registro, catálogo e manifesto, preservando IDs, caminhos, aliases, funções, estados de ativação e evidências existentes.

## Fonte integral da arquitetura coordenadora

A fonte integral da arquitetura coordenadora está em [arquitetura-unificada-acionamento-correferencia-recuperacao-aplicacao.md](./arquitetura-unificada-acionamento-correferencia-recuperacao-aplicacao.md). O protocolo-mestre mantém sua identidade e função próprias; a referência não funde nem substitui os instrumentos relacionados.


---

## Pré-configuração executável do protocolo-mestre

Esta seção é aditiva e mantém integralmente a estrutura precedente. O protocolo-mestre coordena a arquitetura unificada, o instrumento fixo `github-operational` e todos os instrumentos adicionais identificados pelos títulos fornecidos. A inclusão dos dois componentes-base no plano não depende da repetição de seus títulos pelo usuário.

### Fluxo automatizado

1. Receber a demanda em um evento GitHub autorizado.
2. Construir um payload estruturado preservando a demanda original e o destino proposto.
3. Executar `scripts/promptaria_preflight.py` para gerar o plano e suas condições.
4. Executar `scripts/promptaria_resolver.py` contra o diretório `instruments/` para resolver cumulativamente os títulos.
5. Executar `scripts/promptaria_validate_result.py` para validar completude e rastreabilidade do resultado de resolução.
6. Publicar plano e resultado como artefatos verificáveis.
7. Manter qualquer escrita real fora deste fluxo de planejamento, sujeita ao executor específico, à autorização, ao destino permitido e à confirmação exigida.

### Condições de conclusão

A execução integral não será declarada apenas com base na detecção do título, na recuperação, no plano ou no upload do artefato. A conclusão depende de evidência técnica da operação e de validação contra a demanda. Falhas, colisões, conteúdos ausentes e etapas não executadas devem permanecer explícitos.

### Não limitação e não substituição

Todos os títulos válidos fornecidos serão considerados, sem limite numérico arbitrário e sem interromper a busca na primeira correspondência. A exceção de função diversa será avaliada individualmente e não se projeta sobre outros títulos. O protocolo coordena; não absorve nem reescreve a lógica dos instrumentos especializados.
