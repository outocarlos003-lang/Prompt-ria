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
- Validação de destino relativo e bloqueio de caminhos absolutos ou com `..`.
- Artefato JSON com correspondências e estados de rastreabilidade.

## Limites importantes

Esta versão gera um **plano validável**, não executa magicamente as instruções de cada prompt. Não lê conversas arbitrárias do ChatGPT, não conecta automaticamente o GitHub ao conector do ChatGPT e não escreve em Nocturna ou em outros repositórios. A demanda precisa ser transmitida por um evento descrito acima; execução externa exige integração e permissões próprias.

A decisão semântica sobre função diversa não é reduzida a uma heurística lexical: o resultado marca a exceção como pendente de revisão contextual. O workflow não declara executada uma operação quando apenas identificou um título.

## Execução local

`python scripts/promptaria_resolver.py --request request.json --instruments instruments --output promptaria-result.json`

O arquivo de entrada deve conter JSON com `request` e, opcionalmente, `destination` e `dry_run`.
