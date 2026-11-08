# Auditoria operacional inicial da Promptária

- **Escopo observado:** árvore completa da branch `main` no commit `ae021a47d0fa313564bf666f605fc35d09defb6b`, sem truncamento informado pela API.
- **Data da observação:** 2026-10-17.
- **Rastreabilidade:** issue [#15](https://github.com/outocarlos003-lang/Prompt-ria/issues/15).
- **Natureza:** auditoria estática inicial. Não equivale a execução local dos testes nem a prova de efeitos externos.

## Resumo executivo

O repositório já contém resolução por títulos, preparação de solicitações, executor controlado de escrita, validação de resultado, trilha de auditoria com encadeamento de hashes, testes e workflows do GitHub Actions. Portanto, não é correto afirmar que “não existe executor” em sentido geral.

A lacuna principal é de **integração e escopo**: o resolvedor gera um plano e explicitamente informa que não executa a função especializada; o workflow de correferência prepara pedidos estruturados forçando `dry_run=true` e `write_authorized=false`. O executor de `write_text` opera apenas no escopo autorizado por `config/promptaria_permissions.json` e exige confirmação explícita por ID de operação para escrita real. Não há evidência nesta auditoria de que os prompts especializados sejam traduzidos automaticamente em chamadas para executores específicos.

## Classificação dos instrumentos promptuais

Critério aplicado: a descoberta por título e a inclusão em um plano não provam execução da função descrita. Os instrumentos abaixo são **parcialmente automatizados** no fluxo de descoberta/planejamento; a execução semântica própria de cada prompt não está comprovada e permanece uma lacuna. Esta classificação não significa que o prompt integral seja executado automaticamente.

| ID / título canônico | Caminho | Categoria | Evidência atual | Lacuna para automação funcional |
|---|---|---|---|---|
| GitHub operacional — Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas | `instruments/acione-a-promptaria-pelo-github.md` | Parcialmente automatizado | Workflow `promptaria-correfencia.yml` recebe `workflow_dispatch` e comentário `/promptaria`, resolve títulos e publica artefatos | Não executa a função especializada nem aplica mutações a partir do plano |
| Arquitetura unificada de correferência funcional automática | `instruments/arquitetura-unificada-acionamento-correferencia-recuperacao-aplicacao.md` | Parcialmente automatizado | Scripts Python/JavaScript detectam títulos e exceções locais | Necessita demonstrar que a decisão funcional e o prompt integral são ligados a um executor apropriado; semântica ambígua deve continuar bloqueada |
| Arquitetura unificada | `instruments/arquitetura-unificada.md` | Parcialmente automatizado | Incluída como componente-base pelo resolvedor | Coordenação documental não é, por si, execução dos instrumentos coordenados |
| Pré-configuração de correspondência futura e cadeia | `instruments/preconfiguracao-correspondencia-futura-e-cadeia.md` | Parcialmente automatizado | Resolvedor preserva contexto estruturado e plano de seleção | Falta provar que as demandas futuras acionam um caminho executor, com validação de parâmetros e permissões |
| Pré-configuração de sincronização catálogo/sitemap | `instruments/preconfiguracao-sincronizacao-catalogo-sitemap.md` | Parcialmente automatizado | O resolvedor pode incluí-la como pré-configuração padrão | Não há prova de sincronização externa efetiva apenas pela inclusão no plano |
| Protocolo-mestre de acionamento automático | `instruments/protocolo-mestre-acionamento-automatico.md` | Parcialmente automatizado | Incluído como componente-base e usado como regra operacional documental | O protocolo não instala gatilhos universais; depende da integração que carrega e aplica seu conteúdo |
| Protocolo-mestre de execução correta | `instruments/protocolo-mestre-execucao-correta.md` | Parcialmente automatizado | Existe como instrução versionada | Não foi identificado executor específico que transforme todas as etapas do protocolo em ações verificáveis |
| Modelo de instrumento promptual | `instruments/modelo-instrumento-promptual-correferencia.md` | Parcialmente automatizado | Modelo versionado e validado pelo registro | É um template preparado, não uma ativação funcional por si só |
| Protocolo de atualização e integridade | `instruments/protocolo-operacional-atualizacao-integridade-acervo.md` | Parcialmente automatizado | Registra preservação funcional e rastreabilidade | A publicação e habilitação funcional dependem da flag explícita de ativação |
| Nocturna — arquitetura da necessidade | `instruments/nocturna-arquitetura-necessidade-identidade-sistemica.md` | Parcialmente automatizado | Fonte local recuperável e título canônico rastreado | A existência local não comprova acesso ou análise dos acervos externos Nocturna |

## Inventário de mecanismos de execução

| Componente | Estado estático | Evidência | Limitação / próximo passo |
|---|---|---|---|
| `scripts/promptaria_resolver.py` | Implementado; integrado ao workflow | Descobre Markdown, normaliza títulos e mantém correspondências | Correspondência é textual; não basta para inferir equivalência semântica ou autorização |
| `scripts/promptaria_prepare_executor_request.py` | Implementado; preparação apenas | Valida JSON e força simulação sem autorização de escrita | Intencionalmente não habilita escrita real a partir de entrada do workflow |
| `scripts/promptaria_executor.py` | Executor controlado implementado | Valida operação, destino, tamanho, permissões, replay e cadeia de auditoria; possui modo de escrita explícita | O escopo declarado em `config/promptaria_permissions.json` é `write_text` em `artifacts/`; requer teste real controlado para provar efeitos |
| `scripts/promptaria_validate_result.py` | Implementado; integrado | Falha fechado se contrato do plano estiver incompleto ou alegar escrita disponível | Valida o artefato do resolvedor, não a execução semântica do instrumento |
| `scripts/promptaria_audit_anchor.py` | Implementado | Cria/verifica âncora externa de cadeia de auditoria | A âncora exige armazenamento externo configurado; não prova, sozinha, execução de uma operação |
| `.github/scripts/resolver-correferencia.mjs` | Implementado; coberto por testes/workflow | Resolvedor JavaScript de correferência | Verificar paridade com Python nos casos-limite e confirmar que resultados são consumidos pelo fluxo operacional |
| `.github/scripts/validate_promptaria_corref.py` | Implementado; integrado | Validação de integridade e consistência da correferência | Validação estrutural não equivale a execução de prompt |
| `.github/scripts/build_correfencia_execution_bundle.py` | Implementado; integrado ao pacote de testes | Produz pacote de execução/validação | Pacote e artefato não comprovam que ações externas foram realizadas |

## GitHub Actions e CI

Workflows encontrados na árvore completa:

- `.github/workflows/promptaria-correfencia.yml`
- `.github/workflows/promptaria-integracao-pr.yml`
- `.github/workflows/promptaria-preconfig-validation.yml`
- `.github/workflows/promptaria-resolvedor-js.yml`
- `.github/workflows/promptaria-tests.yml`
- `.github/workflows/testes-resolvedor.yml`

A consulta de execuções retornou 536 runs históricas. A execução mais recente observada em `main` era `success` para o workflow `testes-resolvedor.yml`, no commit auditado. Isso comprova somente o resultado daquele run; não significa que todos os workflows ou todas as integrações externas tenham sido exercitados nesta auditoria.

O workflow `promptaria-integracao-pr.yml` implementa merge controlado por comentário exato `/promptaria merge`, associação `OWNER`, PR aberto do mesmo repositório para `main`, espera dos checks e confirmação do SHA antes do merge. Não se deve contornar essas verificações.

## Catálogo e correferência

- O catálogo dinâmico do resolvedor lê arquivos `*.md` em `instruments/` e usa o primeiro cabeçalho `#` como título.
- `tests/manifest.json` existe, mas contém quatro registros e não corresponde a um inventário completo de todos os instrumentos. Não deve ser tratado como catálogo integral.
- O README descreve a descoberta de títulos e a geração de plano; o instrumento operacional também declara que a automação configurada gera um plano JSON e que a execução de lógicas especializadas exige integração explícita.
- A normalização remove acentos, ignora caixa e trata pontuação/separadores, mas sinônimos e aliases não são evidência de equivalência operacional por si sós.
- Não foi encontrada uma evidência estática suficiente para afirmar que todos os instrumentos tenham executor específico ou que suas funções sejam executadas automaticamente.

## Lacunas priorizadas

| Prioridade | Lacuna | Impacto | Encerramento verificável |
|---|---|---|---|
| P0 | Ligar a seleção a contratos explícitos de executor sem tratar similaridade textual como autorização | Risco de ação errada ou alegação falsa de conclusão | Testes de correspondência ambígua/incompatível bloqueiam execução; saída registra candidato, motivo e decisão |
| P0 | Preservar o modo fail-closed e a aprovação explícita para escrita real | Evita mutação não autorizada | Testes demonstram que entrada do usuário não pode elevar `write_authorized` nem sair de `artifacts/` |
| P1 | Inventário canônico completo com aliases validados contra caminhos e títulos físicos | Evita catálogo parcial e aliases órfãos | Cada instrumento Markdown aparece uma vez; caminhos e títulos físicos conferem |
| P1 | Matriz de instrumentos → executor → parâmetros → permissões → evidência | Evita confundir instrução declarativa com automação | Cada instrumento tem executor específico ou lacuna explicitamente registrada |
| P1 | Paridade e regressão entre resolvedores Python e JavaScript | Evita decisões inconsistentes entre pipelines | Fixture comum cobre acentos, pontuação, títulos próximos, ambiguidades e ausência de correspondência |
| P2 | Testes reais controlados para a operação de escrita e reconciliação após interrupção | Prova os efeitos reais sem ampliar escopo | Execução isolada em destino permitido, resultado lido de volta e auditoria verificada |
| P2 | Verificar individualmente todos os workflows ativos e os checks obrigatórios do PR | Evita confundir um run bem-sucedido com CI integral | Run/check de cada workflow pertinente identificado; estados ignorados/bloqueados explicitados |

## Limites desta auditoria

1. A auditoria foi baseada na árvore, nos conteúdos recuperados e nos metadados disponíveis via GitHub; não houve checkout nem execução local do conjunto de testes neste ambiente.
2. A existência de uma execução recente bem-sucedida foi observada, mas os logs de todos os jobs e workflows não foram integralmente inspecionados.
3. Serviços externos, segredos, configurações de ambiente e efeitos de produção não foram executados nem presumidos.
4. Nenhuma funcionalidade é declarada “já automatizada” sem evidência de executor funcional, integração, pré-condições, permissões e resultado observável.
5. Este documento é uma linha de base auditável; a implementação e os testes posteriores devem atualizar as classificações quando houver novas evidências.
