# Promptária — Arquitetura Neural, Rastreável e Integrada

A Promptária preserva a árvore física dos instrumentos e acrescenta uma rede funcional de navegação sobre ela.

## Princípios operacionais

- Conteúdo → caminho → destino → retorno → conexão.
- A página inicial é o núcleo de convergência.
- `Promptária/Index.html` é o índice transversal.
- `Promptária/manifest.json` é a fonte única de verdade da topologia.
- `Promptária/navegacao-neural.js` materializa entrada, retorno, anterior, próximo e pesquisa nas páginas.
- A pesquisa atravessa títulos, caminhos e conteúdo dos instrumentos catalogados.
- A rastreabilidade registra demanda, origem, instrumento, operação, transformação, artefato, destino, referências, validação e resultado.
- O diretório de um instrumento não determina automaticamente o destino de uma operação.
- Nocturna só é considerado destino quando houver determinação explícita ou inequivocamente determinada.

## Topologia

`index.html` → `Promptária/Index.html` ↔ Arquitetura Unificada de Acionamento, Correferência, Recuperação e Aplicação de Instrumentos Promptuais.

O instrumento catalogado mantém caminho de entrada e retorno à interface principal.

## Integridade

A coleção catalogada contém um instrumento: a Arquitetura Unificada de Acionamento, Correferência, Recuperação e Aplicação de Instrumentos Promptuais. O manifesto é a fonte única de verdade da navegação.

A validação verifica:

1. existência do conteúdo;
2. existência de caminho e destino;
3. existência de retorno;
4. validade das referências;
5. integridade das dependências;
6. rastreabilidade de produção;
7. ausência de páginas órfãs;
8. coerência entre árvore física e rede navegacional;
9. funcionamento estrutural de ponta a ponta.

Consulte `Promptária/rastreabilidade-producao.json` para o registro da operação de saneamento.

## Garantia operacional

- `manifest.json` define a identidade canônica dos instrumentos.
- Título, aliases e capacidades sustentam a correferência semântica.
- `navegacao-neural.js` materializa a rede no navegador.
- `verificador-integridade.mjs` verifica catálogo, arquivos, arestas, reciprocidade, sitemap, camada navegacional e rastreabilidade.
- O workflow `.github/workflows/promptaria-integrity.yml` executa a verificação em alterações da `main` e em pull requests.
- A validação é *fail-closed*: uma inconsistência estrutural produz falha.
- Instrumentos futuros devem ser registrados no catálogo; a navegação e a correferência os incorporam a partir dessa fonte única.

## Instrumentos catalogados

- **Arquitetura Unificada de Acionamento, Correferência, Recuperação e Aplicação de Instrumentos Promptuais**
  - Caminho: `Promptária/Arquitetura-Unificada-de-Acionamento-Correferencia-Recuperacao-e-Aplicacao-de-Instrumentos-Promptuais/Index.html`.
  - Registro canônico: `instrumento-12` em `Promptária/manifest.json`.

## Regra de evolução

Adicionar, renomear, mover ou remover um instrumento exige manter sincronizados:

**ID → título canônico → aliases → capacidades → caminho → entrada → anterior → próximo → conteúdo → sitemap → referências → validação.**
