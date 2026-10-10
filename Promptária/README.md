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

`index.html` → `Promptária/Index.html` ↔ instrumentos catalogados.

O núcleo conecta cada instrumento por caminhos de entrada, retorno e interface principal. Instrumentos relacionados permanecem autônomos.

## Integridade

O manifesto é a fonte única de verdade da navegação. A validação verifica:

1. existência do conteúdo;
2. existência de caminho e destino;
3. existência de retorno;
4. validade das referências;
5. integridade das dependências;
6. rastreabilidade de produção;
7. ausência de páginas órfãs;
8. coerência entre árvore física e rede navegacional;
9. funcionamento estrutural de ponta a ponta.

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

- **ACIONE A PROMPTÁRIA PELO GITHUB PARA INSERIR, RECUPERAR E APLICAR DEMANDAS**
  - Caminho: `Promptária/Acione-a-Promptaria-pelo-GitHub-para-Inserir-Recuperar-e-Aplicar-Demandas/Index.html`.
  - Registro canônico: `instrumento-13` em `Promptária/manifest.json`.
  - Relação: instrumento de acionamento, recuperação, personalização e execução, relacionado à arquitetura coordenadora sem fusão de identidades.

- **INSTRUMENTO PROMPTUAL — TUDO SE CONECTA, TUDO SE RASTREIA E TUDO SE INTEGRA**
  - Caminho: `Promptária/INSTRUMENTO-PROMPTUAL-Tudo-se-conecta-tudo-se-rastreia-e-tudo-se-integra/Index.html`.
  - Registro canônico: `instrumento-14` em `Promptária/manifest.json`.
  - Relação: integração de rastreabilidade navegacional, produção e integridade sistêmica, mantendo identidade autônoma.

- **ORGANIZAÇÃO INTELIGENTE DE ZIP NO DIRETÓRIO DO GITHUB**
  - Caminho: `Promptária/Organizacao-Inteligente-de-ZIP-no-Diretorio-do-GitHub/Index.html`.
  - Registro canônico: `instrumento-15` em `Promptária/manifest.json`.
  - Relação: instrumento para integração controlada de ZIP, preservação arquitetural e validação rastreável.



## Regra de evolução

Adicionar, renomear, mover ou remover um instrumento exige manter sincronizados:

**ID → título canônico → aliases → capacidades → caminho → entrada → anterior → próximo → conteúdo → sitemap → referências → validação.**


- **DIRETRIZ FUNDAMENTAL DE EXECUÇÃO EDITORIAL, INTEGRIDADE TEXTUAL E ARQUITETURA HIERÁRQUICA**
  - Caminho: `Promptária/Diretriz-Fundamental-de-Execucao-Editorial-Integridade-Textual-e-Arquitetura-Hierarquica/Index.html`.
  - Registro canônico: `instrumento-16` em `Promptária/manifest.json`.
  - Relação: execução editorial seriada, preservação textual e hierarquia coleção–blocos–capítulos, mantendo identidade autônoma.


- **ADAPTAÇÃO E EXECUÇÃO EXTENSIVAS DOS INSTRUMENTOS PROMPTUAIS — PROMPT-MATRIZ DE ADAPTAÇÃO EXTENSIVA MULTIDIRETÓRIO**
  - Caminho: `Promptária/Adaptacao-e-Execucao-Extensiva-Multidiretorio/Index.html`.
  - Registro canônico: `instrumento-17` em `Promptária/manifest.json`.
  - Relação: adaptação conservativa, operações multidiretório, resolução de destinos, materialização, coordenação e rastreabilidade; identidade autônoma.
