# Promptária — Arquitetura Neural, Rastreável e Integrada

A Promptária preserva a árvore física dos instrumentos e acrescenta uma rede funcional de navegação sobre ela.

## Princípios operacionais

- Conteúdo → caminho → destino → retorno → conexão.
- A página inicial é o núcleo de convergência.
- Promptária/Index.html é o índice transversal.
- Promptária/manifest.json é a fonte única de verdade da topologia.
- Promptária/navegacao-neural.js materializa entrada, retorno, anterior, próximo e pesquisa em todas as páginas.
- A pesquisa atravessa títulos, caminhos e conteúdo dos 10 instrumentos.
- A rastreabilidade de produção registra demanda, origem, instrumento, operação, transformação, artefato, destino, referências, validação e resultado.
- O diretório do instrumento não determina automaticamente o destino de uma operação.
- Nocturna só é considerado destino quando houver determinação explícita ou inequivocamente determinada.

## Topologia

index.html → Promptária/Index.html → qualquer instrumento → anterior/próximo → ciclo → núcleo.

Cada instrumento mantém também caminho de retorno à interface principal.

## Integridade

A reorganização preserva os instrumentos existentes e concentra a nova conectividade em uma camada compartilhada, evitando duplicação de lógica e mantendo o manifesto como fonte única de verdade.

A validação deve verificar simultaneamente:

1. existência do conteúdo;
2. existência de caminho;
3. existência de destino;
4. existência de retorno;
5. validade das referências;
6. integridade das dependências;
7. rastreabilidade de produção;
8. ausência de órfãos introduzidos;
9. coerência entre árvore física e rede navegacional;
10. funcionamento de ponta a ponta.

Consulte Promptária/rastreabilidade-producao.json para o registro da transformação.
