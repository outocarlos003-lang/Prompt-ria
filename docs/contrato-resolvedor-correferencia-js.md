# Contrato de reconstrução — resolvedor JavaScript de correferência

**Estado:** especificação derivada dos testes existentes; não é implementação recuperada nem prova de comportamento executável.

## Localização e exportações exigidas

O teste `tests/resolver-correferencia.test.mjs` importa `.github/scripts/resolver-correferencia.mjs` e espera estas exportações:

- `buildReferenceIndex(instruments)`
- `resolveMentions(request, instruments, index?)`
- `resolveReference(reference, index)`
- `resolveRequest(request, instruments)`
- `FIXED_OPERATIONAL_INSTRUMENT`
- `FIXED_COORDINATOR_TITLE`
- `FUNCTION_STATUS`

O arquivo de entrada da raiz `resolver-correferencia.mjs` reexporta esse módulo ausente. Portanto, criar apenas a entrada da raiz não resolve a dependência.

## Comportamentos exigidos pelos testes

1. **Identidade canônica:** reconhecer título, ID, caminho e alias; normalizar caixa, acentos, hífens e pontuação sem perder os offsets das menções no texto original.
2. **Ambiguidade:** colisões entre títulos/aliases não devem ativar arbitrariamente um candidato. O resultado precisa preservar os IDs candidatos e usar `ambiguous_title_alias`, `ambiguous_title` ou o estado equivalente definido pelo cenário.
3. **Ativação funcional:** uma menção genérica ativa a função própria (`own`). Uma atribuição explícita de função diversa (`diverse`) só afeta a menção/título correspondente, não instrumentos vizinhos ou menções repetidas posteriores.
4. **Menções múltiplas:** resolver cumulativamente todos os títulos identificáveis e preservar rastreabilidade entre os instrumentos.
5. **Referências explícitas:** suportar `instrument_id:<id>` e `instrument_path:<path>`; referências inexistentes ou desativadas não podem ser ativadas.
6. **Coordenador e instrumento operacional fixo:** `resolveRequest` expõe `coordinator` e `operational_fixed`; demanda não vazia pode ativá-los conforme o contrato testado. Uma requisição vazia não inventa demanda nem ativa o instrumento operacional fixo. As operações fixas esperadas são `inserir`, `recuperar` e `aplicar`.
7. **Paridade:** executar os cenários de `tests/fixtures/correference-parity.json` e produzir, para cada menção, pelo menos `title`, `activation` e `function_status` iguais ao resultado esperado.
8. **Catálogo:** preservar IDs e caminhos distintos; títulos normalizados duplicados devem ser reportados como ambíguos, com todos os candidatos rastreáveis.

## Campos observados nos resultados esperados

As asserções verificam, conforme a função chamada, campos como `instrument_id`, `activation`, `function_status`, `match_type`, `candidates`, `path`, `start`, `end`, `exception_scope`, `operations`, `transmitted`, `matches`, `activated`, `multiple_titles` e `traceability`. A implementação deve manter os formatos e nomes exatos que os testes exigem.

## Validação pendente

- Implementar ou recuperar o módulo em `.github/scripts/resolver-correferencia.mjs`.
- Executar `node --test tests/resolver-correferencia.test.mjs` num checkout da branch.
- Executar a suíte completa depois de resolver as dependências ausentes.
- Não declarar testes aprovados até que a execução real confirme isso.

Esta especificação resume expectativas verificadas por leitura estática do teste. Não substitui o teste nem afirma que o resolvedor está implementado.
