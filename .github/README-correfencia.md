# Validação automática de correferência funcional

Esta área contém a implementação técnica da correferência. Os instrumentos promptuais armazenados em `Promptária/` não são reescritos pelo validador.

## Regra implementada

Para cada ocorrência de um título reconhecido:

1. a existência do título estabelece a correferência;
2. a menção genérica preserva a função própria;
3. silêncio, ausência de descrição funcional e ambiguidade não constituem função diversa;
4. função diversa somente é reconhecida por atribuição expressa ou contexto local inequivocamente suficiente;
5. a exceção pertence à ocorrência que a qualifica e não se projeta a outros títulos;
6. múltiplos títulos permanecem independentes, cumulativos, coordenáveis, simultâneos e não exclusivos;
7. a validação não modifica o conteúdo dos instrumentos;
8. a correspondência usa limites de frase/palavra para evitar casar um título apenas como substring de outro texto;
9. o trecho casado e o contexto são preservados no texto original; a normalização é usada somente para comparação;
10. o `manifest.json` é confrontado com a árvore física quando está presente.

## Catálogo e fonte de verdade

O validador descobre os instrumentos fisicamente e, se existir `Promptária/manifest.json`, verifica que:

- cada caminho físico está declarado;
- cada título físico coincide com o título declarado;
- divergências tornam o resultado `catalog_inconsistente`.

Isso impede que o manifesto diga uma coisa enquanto a validação consulta outra.

## Plano de execução

O resultado possui `execution_plan`. Ele identifica, para cada instrumento ativo, o arquivo que deve ser recuperado/executado e quantas ocorrências o acionaram.

Importante: **plano de execução não significa que GitHub Actions execute o HTML como um instrumento**. O validador não inventa uma execução que não existe. Para execução real, uma camada externa precisa consumir o `execution_plan`, recuperar o conteúdo do instrumento e aplicar suas instruções.

## Recuperação dos instrumentos acionados

Após a validação, `build_correfencia_execution_bundle.py` recupera o conteúdo dos instrumentos presentes no `execution_plan` e produz `correfencia-execution-bundle.json`. Assim, o fluxo deixa de parar na identificação: ele também materializa o conjunto de instruções que uma camada executora externa deve consumir.

A aplicação efetiva dessas instruções sobre a requisição continua sendo responsabilidade do runtime que integra a Promptária ao modelo/agente. O repositório não finge que um HTML foi “executado” apenas por ter sido identificado.

## GitHub Actions

O workflow `.github/workflows/correfencia-funcional.yml` executa:

- **pull request/push:** testes, catálogo, manifesto, sitemap e navegação;
- **workflow_dispatch:** validação de um `prompt` fornecido manualmente;
- **repository_dispatch:** validação de `client_payload.prompt` recebido por integração autorizada.

As alterações em `Promptária/**` também disparam o workflow em `push`, evitando que mudanças de títulos/instrumentos escapem da validação.

Exemplo de payload:

    {"prompt":"Instrumento A + Instrumento B: executar a requisição"}

GitHub Actions não observa autonomamente conversas do ChatGPT. O texto precisa ser efetivamente transmitido ao workflow.

## Resultado

O JSON conserva, por ocorrência:

- título;
- texto original correspondente;
- instrumento;
- correferência;
- estado da função;
- atividade;
- escopo local da exceção;
- contexto original;
- plano de execução cumulativo.

Todas as correspondências permanecem representadas; não há redução automática para um único instrumento.


## Complementação arquitetural interconectada

A correferência agora possui uma camada complementar de coordenação que **não substitui nenhum elemento estrutural existente**. Ela adiciona ao resultado o bloco `coordination`, preservando `schema_version`, `rule`, `matches`, `active_instruments`, `exceptions` e `execution_plan`.

A especificação completa está em [`.github/README-correfencia-arquitetura.md`](README-correfencia-arquitetura.md).

Essa camada conecta título e requisição personalizada, recuperação efetiva pelo GitHub, instrumento coordenador, instrumento fixo previsto, coleção aberta de instrumentos adicionais, interpretação conjunta, contextualização, parametrização, adaptação, aplicação conjunta, origem, destino, operação multidiretório, regra especial para Nocturna, resultados intermediários, rastreabilidade e validação final.

A quantidade de instrumentos adicionais é deliberadamente **não limitada**. Cada título adicional reconhecido é uma unidade independente; repetições são ocorrências da mesma unidade. Nenhuma identidade adicional é presumida somente pelo título: a identidade operacional depende do conteúdo recuperado.

A nova camada também não transforma `active` ou `execution_plan` em prova de execução externa. Eles representam identificação/planejamento e recuperação. A aplicação efetiva continua pertencendo ao runtime que consome o pacote.
