# Validação automática de correferência funcional

Esta área contém **somente a implementação técnica** da correferência. Os instrumentos promptuais armazenados em `Promptária/` não são reescritos por este validador.

## Regra implementada

Para cada ocorrência de um título reconhecido:

1. a existência do título estabelece a correferência;
2. a menção genérica preserva a função própria;
3. silêncio, ausência de descrição funcional e ambiguidade não constituem função diversa;
4. função diversa somente é reconhecida por atribuição expressa ou contexto local inequivocamente suficiente;
5. a exceção pertence à ocorrência que a qualifica e não se projeta a outros títulos;
6. múltiplos títulos permanecem independentes, cumulativos, coordenáveis, simultâneos e não exclusivos;
7. a validação não modifica o conteúdo dos instrumentos.

A implementação também distingue **título**, **ocorrência**, **instrumento**, **função própria**, **exceção local** e **conjunto cumulativo de correspondências**, evitando transformar várias correferências em uma seleção única.

## Limite da heurística

A classificação automática não pretende inferir intenção subjetiva. Ela procura marcadores textuais suficientes para caracterizar desvio funcional. Diante de incerteza, preserva a correferência e a função própria.

O contexto usado para a exceção é local à ocorrência. Isso evita que uma atribuição diversa feita para um título contamine outra ocorrência ou outro instrumento.

## Catálogo

O validador lê apenas metadados dos diretórios imediatos de `Promptária/` que contenham `Index.html`. Essa leitura serve para localizar títulos e caminhos; **nenhum arquivo de instrumento é alterado**.

## GitHub Actions

O workflow `correfencia-funcional.yml` executa:

- **pull request/push:** testes automatizados da função de correferência;
- **workflow_dispatch:** validação de um `prompt` fornecido manualmente;
- **repository_dispatch:** validação de `client_payload.prompt` recebido por integração autorizada.

Exemplo de payload:

```json
{"prompt":"Instrumento A + Instrumento B: executar a requisição"}
```

GitHub Actions não observa autonomamente conversas do ChatGPT. O texto precisa ser efetivamente transmitido ao workflow.

## Resultado

O artefato JSON conserva, por ocorrência:

- título;
- texto correspondente;
- instrumento;
- correferência;
- estado da função;
- atividade;
- escopo local da exceção;
- contexto local.

Todas as correspondências permanecem representadas; não há redução automática para um único instrumento.
