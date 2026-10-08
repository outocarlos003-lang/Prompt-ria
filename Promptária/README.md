# Promptária — Arquitetura Navegacional e Rastreabilidade

A Promptária preserva a árvore física dos instrumentos e acrescenta uma rede navegacional sobre ela.

## Fonte única de verdade

- `manifest.json`: catálogo, nós e arestas navegacionais.
- `Index.html`: núcleo de convergência e pesquisa transversal.
- `sitemap.xml`: enumeração navegacional dos nós publicados.
- Cada `*/Index.html`: conteúdo integral do instrumento, preservado sem fusão.

## Invariantes

1. Se existe conteúdo, existe caminho.
2. Se existe caminho, existe destino.
3. Se existe destino, existe retorno.
4. Se existe relação, existe conexão.
5. A pesquisa atravessa todos os instrumentos.
6. A árvore física não substitui a rede funcional.

A organização evita duplicar o conteúdo dos instrumentos: o manifesto referencia os artefatos existentes e a interface deriva sua navegação dessas referências.
