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

A inclusão automática é uma préconfiguração de reconhecimento e planejamento, não uma alegação de que as instruções especializadas foram executadas. O resolvedor rejeita `dry_run` que não seja booleano JSON; o padrão é `true`. Um pedido `dry_run: false` exige `write_authorized: true` e `destination` explícito, mas ainda é recusado na prática até existir um executor de escrita integrado: essa versão apenas gera planos e não modifica o destino. A execução real continua dependente de um evento autorizado, permissões e integração apropriada. Exceções semânticas de função diversa exigem revisão contextual; o resolvedor não as decide por mera comparação lexical.

Para acionar uma demanda por comentário, use `/promptaria <demanda completa>` em uma issue. Para execução manual, abra Actions → “Promptária - correferência funcional por título” → Run workflow. O artefato JSON indica componentes obrigatórios ausentes, títulos reconhecidos e estados de rastreabilidade.


## Executor especializado com permissões e auditoria

O executor `scripts/promptaria_executor.py` é uma etapa separada do resolvedor: reconhecer um instrumento ou incluí-lo no plano nunca executa seu conteúdo. O executor aceita apenas a operação estruturada `write_text`; não interpreta prompts recuperados como comandos nem executa shell.

- O padrão é `dry_run: true`; a simulação não grava o destino.
- A execução real exige simultaneamente `dry_run: false`, `write_authorized: true` e `--confirm-operation` com o mesmo `operation_id` da solicitação.
- `config/promptaria_permissions.json` limita a escrita a arquivos sob `artifacts/` e impõe limite de tamanho.
- O destino é validado como caminho relativo POSIX, com proteção contra traversal, `.git`, caminhos absolutos, links simbólicos e arquivos não regulares.
- A escrita autorizada é atômica e o executor compara o SHA-256 do conteúdo solicitado com o resultado gravado.
- Cada operação aceita é registrada em `.promptaria/audit.jsonl`, com identificador, modo, destino, estado e hashes.

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
