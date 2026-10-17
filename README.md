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
- Inclusão do componente fixo quando o arquivo existe.
- Validação estrita de destino relativo: bloqueia caminhos absolutos, segmentos `..`, segmentos vazios, `.`, `.git`, separadores Windows e caracteres de controle.
- Validação estrita de `dry_run` e autorização explícita para qualquer pedido de modo não simulado.
- Artefato JSON com correspondências e estados de rastreabilidade.

## Limites importantes

Esta versão gera um **plano validável**, não executa magicamente as instruções de cada prompt. Não lê conversas arbitrárias do ChatGPT, não conecta automaticamente o GitHub ao conector do ChatGPT e não escreve em Nocturna ou em outros repositórios. A demanda precisa ser transmitida por um evento descrito acima; execução externa exige integração e permissões próprias.

A decisão semântica sobre função diversa não é reduzida a uma heurística lexical: o resultado marca a exceção como pendente de revisão contextual. O workflow não declara executada uma operação quando apenas identificou um título.

## Execução local

`python scripts/promptaria_resolver.py --request request.json --instruments instruments --output promptaria-result.json`

O arquivo de entrada deve conter JSON com `request` e, opcionalmente, `destination` e `dry_run`.

## Protocolo-mestre e préconfiguração padrão

O instrumento `instruments/protocolo-mestre-acionamento-automatico.md` preserva o modelo genérico com seus quatro elementos estruturais e serve como préconfiguração para demandas futuras. O resolvedor inclui automaticamente, em cada plano, os três componentes-base: a arquitetura coordenadora, o protocolo-mestre e o instrumento operacional do GitHub. Títulos adicionais mencionados são todos recuperados por correspondência normalizada.

A inclusão automática é uma préconfiguração de reconhecimento e planejamento, não uma alegação de que as instruções especializadas foram executadas. O resolvedor rejeita `dry_run` que não seja booleano JSON; o padrão é `true`. A escrita é tratada por um executor separado e nunca é disparada apenas porque um título ou prompt foi recuperado. No workflow GitHub Actions, a integração do executor é deliberadamente restrita à simulação; escrita real não é autorizada pelo workflow. Exceções semânticas de função diversa exigem revisão contextual; o resolvedor não as decide por mera comparação lexical.

Para acionar uma demanda por comentário, use `/promptaria <demanda completa>` em uma issue. Para execução manual, abra Actions → “Promptária - correferência funcional por título” → Run workflow. O artefato JSON indica componentes obrigatórios ausentes, títulos reconhecidos e estados de rastreabilidade.


## Cadeia de integridade da auditoria

Os novos registros incluem `audit_prev_hash` e `audit_hash`, calculados a partir de JSON canônico. O executor verifica a cadeia disponível e bloqueia alterações detectáveis, reordenação, JSON inválido e última linha incompleta. **Uma cadeia local, isoladamente, não consegue detectar com garantia a remoção de um sufixo completo nem a substituição integral do arquivo.** Registros legados sem hash só podem aparecer antes do início da cadeia; o primeiro registro encadeado ancora os bytes do histórico anterior, mas não protege contra truncamento posterior sem uma âncora externa. Operações de escrita real agora registram `write_intent` antes da mutação e `executed` após a validação; se a conclusão desaparecer ou a execução for interrompida, a reutilização do mesmo `operation_id` falha fechada e exige reconciliação manual. Para detectar remoção de histórico, exporte periodicamente âncoras para armazenamento externo confiável, protegido contra alteração pela identidade do executor.

## Validação de resultados e teste ponta a ponta

Após a resolução, `scripts/promptaria_validate_result.py` verifica o contrato do artefato: esquema esperado, presença dos três componentes obrigatórios, recuperação de conteúdo, estados que não alegam execução e indisponibilidade de escrita no resolvedor. A validação falha de forma explícita se faltar qualquer componente obrigatório ou se o JSON declarar uma execução que não ocorreu.

O workflow `.github/workflows/promptaria-tests.yml` executa a suíte de regressão e um smoke test com os instrumentos reais do repositório: chama o resolvedor e valida o JSON resultante. Assim, a integração verifica não apenas testes com fixtures, mas também se a coleção efetiva de instrumentos satisfaz o contrato obrigatório.

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
