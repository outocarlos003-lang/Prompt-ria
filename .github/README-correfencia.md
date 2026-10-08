# Validação de correferência funcional

O workflow **Correferência funcional dos instrumentos promptuais** materializa a regra de que:

1. uma menção genérica a um título existente em `Promptária/` estabelece correferência com o respectivo instrumento;
2. a correferência reconhece a função própria do instrumento;
3. a ausência de explicitação da função não constitui função diversa;
4. a função diversa somente é marcada quando há atribuição expressa ou contexto inequivocamente desviador;
5. títulos diferentes encontrados na mesma requisição permanecem individualmente ativos e podem compor o mesmo fluxo.

## Entradas

O workflow pode receber uma requisição por `workflow_dispatch` ou por `repository_dispatch` com o tipo `promptaria-correfencia` e payload contendo:

```json
{"prompt":"..."}
```

O validador lê automaticamente os diretórios imediatos de `Promptária/` que contenham `Index.html`; assim, novos instrumentos passam a integrar o catálogo sem uma lista manual.

## Limite importante

GitHub Actions não recebe, por si só, o texto digitado em uma conversa do ChatGPT. Para uma integração externa, o conector/cliente que possuir o texto deve disparar `repository_dispatch` com o campo `prompt`. Este workflow fornece o ponto de entrada e a validação, mas não cria uma observabilidade inexistente no conector.

A validação é conservadora: ela não inventa função diversa por silêncio ou ambiguidade.
