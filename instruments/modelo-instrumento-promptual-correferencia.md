---
id: promptaria-instrument-template
title: MODELO FICTÍCIO — INSTRUMENTO PROMPTUAL DE CORREFERÊNCIA EXTENSIVA
aliases:
  - modelo de instrumento promptual
  - instrumento modelo
  - template promptual
  - modelo de correferência
keywords:
  - modelo
  - template
  - correferência
  - identificação extensiva
  - título
  - prompt
  - função
  - arquivo
  - nó
  - relação
---
# MODELO FICTÍCIO — INSTRUMENTO PROMPTUAL DE CORREFERÊNCIA EXTENSIVA

## Finalidade

Este instrumento é um modelo fictício e normativo para novos instrumentos promptuais da Promptária. Seu propósito é demonstrar a identificação extensiva necessária para que um instrumento possa ser descoberto por título, prompt, alias ou palavra-chave e, em seguida, relacionado a sua função, arquivos, operações, nós e instrumentos participantes.

## Contrato de identidade

Todo instrumento posterior deverá possuir, no mínimo:

- `id` estável e único;
- título canônico inequívoco;
- aliases e termos de acionamento;
- palavras-chave de descoberta;
- função própria e responsabilidades delimitadas;
- arquivo Markdown de origem;
- arquivos, scripts, testes ou configurações relacionados;
- relações explícitas com outros instrumentos e componentes;
- operações que pode orientar ou participar;
- nó de interface quando for exibido no site.

A fonte canônica dessas relações é `config/instrument-registry.json`. O catálogo público é derivado dessa fonte e o manifesto de execução deve apontar para o mesmo identificador.

## Correferência funcional

A correspondência deverá ocorrer cumulativamente. Uma menção ao título canônico, a um alias, a uma palavra-chave ou a uma função compatível pode identificar este instrumento, mas a seleção final deverá confrontar todas as evidências disponíveis.

A cadeia mínima é:

`termo/prompt → título ou alias → id → função → arquivo → operação → relação → resultado → validação`.

A identificação não autoriza execução por si só. Primeiro deve ser determinada a correspondência; depois devem ser verificadas a função, as dependências, o escopo da solicitação e as autorizações necessárias.

## Relações obrigatórias

Para cada instrumento novo, procure representar relações do tipo:

- `title -> id`;
- `alias -> id`;
- `keyword -> function`;
- `function -> file`;
- `file -> operation`;
- `instrument -> interface-node`;
- `instrument -> related-instrument`.

Quando uma relação não puder ser comprovada, registre-a como pendente e não a apresente como funcional.

## Operação futura

O resolvedor contextual deverá preservar todas as correspondências suportadas pela solicitação, sem interromper na primeira. O executor somente recebe uma operação depois que a correspondência, a integridade do pacote e as condições de execução tiverem sido verificadas.

A automação é de **pré-configuração e correspondência**, não de execução irrestrita. Escrita, remoção, publicação, merge ou outras ações externas continuam condicionadas às autorizações e aos controles do sistema.

## Modelo de extensão

Ao inserir um instrumento posterior:

1. copie este modelo como ponto de partida;
2. substitua identidade, título, aliases e palavras-chave;
3. declare a função própria;
4. relacione arquivos e operações reais;
5. declare os instrumentos relacionados;
6. registre o nó de interface, se houver;
7. inclua o instrumento no registro canônico;
8. confirme sua presença no manifesto e catálogo derivados;
9. execute as validações de correspondência e integridade;
10. somente então considere o instrumento pronto para integração.

## Critério de conclusão

Um instrumento não é considerado integrado apenas porque seu Markdown existe. Ele deverá ser encontrável, identificável, relacionado aos recursos corretos, representado no catálogo, resolvível pelo sistema e validado pelas automações correspondentes.
