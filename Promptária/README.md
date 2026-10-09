# Promptária — Arquitetura Neural, Rastreável e Integrada

A Promptária preserva a árvore física dos instrumentos e acrescenta uma rede funcional de navegação sobre ela.

## Princípios operacionais

- Conteúdo → caminho → destino → retorno → conexão.
- A página inicial é o núcleo de convergência.
- Promptária/Index.html é o índice transversal.
- Promptária/manifest.json é a fonte única de verdade da topologia.
- Promptária/navegacao-neural.js materializa entrada, retorno, anterior, próximo e pesquisa em todas as páginas.
- A pesquisa atravessa títulos, caminhos e conteúdo de todos os instrumentos catalogados.
- A rastreabilidade de produção registra demanda, origem, instrumento, operação, transformação, artefato, destino, referências, validação e resultado.
- O diretório do instrumento não determina automaticamente o destino de uma operação.
- Nocturna só é considerado destino quando houver determinação explícita ou inequivocamente determinada.

## Topologia

index.html → Promptária/Index.html → Instrumento Promptual de Ensaio ↔ Arquitetura Unificada de Acionamento, Correferência, Recuperação e Aplicação de Instrumentos Promptuais → núcleo.

Cada instrumento mantém caminho de retorno à interface principal.

## Integridade

A coleção catalogada contém o Instrumento Promptual de Ensaio e a nova Arquitetura Unificada de Acionamento, Correferência, Recuperação e Aplicação de Instrumentos Promptuais. O manifesto permanece como fonte única de verdade da navegação.

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

## Garantia operacional

A Promptária não depende apenas de convenções humanas para manter sua rede íntegra.

- `manifest.json` define a identidade canônica dos instrumentos.
- Título, aliases e capacidades sustentam a correferência semântica.
- `navegacao-neural.js` materializa a rede no navegador.
- `verificador-integridade.mjs` verifica catálogo, arquivos, arestas, reciprocidade, sitemap, camada navegacional e rastreabilidade.
- O workflow `.github/workflows/promptaria-integrity.yml` executa essa verificação em alterações da `main` e em pull requests.
- A validação é *fail-closed*: uma inconsistência estrutural produz falha, em vez de ser silenciosamente aceita.
- Instrumentos futuros devem ser registrados no catálogo; a arquitetura de navegação e correferência os incorpora a partir dessa fonte única.

### Regra de evolução

Adicionar, renomear, mover ou remover um instrumento exige manter sincronizados:

**ID → título canônico → aliases → capacidades → caminho → entrada → anterior → próximo → conteúdo → sitemap → referências → validação.**

O objetivo é reduzir a possibilidade de um instrumento existir fisicamente sem existir funcionalmente, ou ser mencionado funcionalmente sem possuir uma referência navegável e rastreável.

## Instrumentos catalogados

- **Instrumento Promptual de Ensaio** — delimitação do tema, formulação da tese, arquitetura argumentativa, redação, revisão e validação de ensaios.
  - Caminho: `Promptária/Instrumento-Promptual-de-Ensaio/Index.html`.
  - Registro canônico: `instrumento-11` em `Promptária/manifest.json`.
- **ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS: ACIONAMENTO COORDENADO DE INSTRUMENTOS PROMPTUAIS E ARQUITETURA DE ACIONAMENTO, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS, COM CORREFERÊNCIA FUNCIONAL AUTOMÁTICA POR TÍTULOS DOS INSTRUMENTOS PROMPTUAIS, NA QUAL A MENÇÃO GENÉRICA IDENTIFICA O INSTRUMENTO, PRESERVA SUA FUNÇÃO PRÓPRIA E ACIONA SUA EXECUÇÃO, SALVO ATRIBUIÇÃO ESPECÍFICA E INEQUÍVOCA DE FUNÇÃO DIVERSA, COM RECONHECIMENTO MÚTUO, CUMULATIVO, COORDENADO E SIMULTÂNEO DE MÚLTIPLOS TÍTULOS**
  - Caminho: `Promptária/Arquitetura-Unificada-de-Acionamento-Correferencia-Recuperacao-e-Aplicacao-de-Instrumentos-Promptuais/Index.html`.
  - Registro canônico: `instrumento-12` em `Promptária/manifest.json`.
