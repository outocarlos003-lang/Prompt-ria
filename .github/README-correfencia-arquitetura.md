# Complementação interconectada da correferência funcional automática por títulos

Esta especificação complementa, sem substituir, a implementação existente de **correferência funcional automática por títulos**. Nenhuma regra estrutural existente é removida: catálogo físico, descoberta por `<title>`, aliases, normalização, limites de frase/palavra, preservação de contexto original, classificação de função própria/diversa, exceção local, múltiplos títulos cumulativos, `execution_plan`, validação do manifesto e materialização do pacote de execução permanecem válidos.

A complementação conecta a correferência a uma arquitetura de **acionamento → recuperação → interpretação → contextualização → parametrização → adaptação → aplicação → execução → validação → resultado**, sem transformar a correferência em um executor fictício.

## 1. Unidade de acionamento

Cada título é simultaneamente referência nominal, identificador operacional, ponto de entrada, chave de acesso e mecanismo de acionamento.

O título, quando escrito no ChatGPT juntamente com a requisição personalizada, identifica o instrumento correspondente e relaciona a estrutura estável à demanda concreta.

A requisição personalizada não é parte da identidade do instrumento. Ela fornece a demanda, objetivo, requisitos, restrições e condições variáveis da aplicação.

A cadeia é:

**título → identificação/acionamento → requisição → localização GitHub → recuperação → instruções/lógica → demanda → contexto → contextualização → parametrização → adaptação → aplicação → execução → resultado.**

O título não é apenas uma etiqueta e não precisa aparecer isoladamente: ele integra a unidade de acionamento formada com a requisição personalizada.

## 2. Correferência preservada

A complementação mantém integralmente a regra atual:

1. a ocorrência reconhecida do título estabelece correferência;
2. a menção genérica preserva a função própria;
3. silêncio, ausência de descrição funcional e ambiguidade não criam função diversa;
4. atribuição diversa somente é reconhecida por indicação expressa ou contexto local inequivocamente suficiente;
5. a exceção é local à ocorrência;
6. títulos múltiplos permanecem independentes, cumulativos, coordenáveis, simultâneos e não exclusivos;
7. nenhuma regra de coordenação funde os instrumentos;
8. a correferência continua sem modificar o conteúdo dos instrumentos.

A correferência identifica unidades. A coordenação estabelece relações entre unidades já identificadas.

## 3. Arquitetura coordenada

### 3.1 Instrumento coordenador

O título estrutural é **Acionamento Coordenado de Instrumentos Promptuais**.

Ele exerce orientação, coordenação e articulação.

Seu conteúdo não é presumido pelo título. Quando presente no catálogo, deve ser recuperado do GitHub e usado como fonte operacional. Quando ausente, a ausência é registrada como `catalog_missing`, sem inventar conteúdo nem alterar instrumentos existentes.

### 3.2 Instrumentos promptuais adicionais

Todo título adicional fornecido pelo usuário é tratado como identificador de uma unidade promptual própria.

O sistema reconhece o título, localiza o instrumento, recupera seu conteúdo efetivo, determina identidade/finalidade/instruções/lógica pelo conteúdo recuperado, preserva a unidade e a incorpora à coordenação.

O título sozinho não autoriza presumir identidade, finalidade, função, conteúdo ou lógica.

### 3.3 Instrumento fixo

O título arquiteturalmente previsto é **Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas**.

Sua identidade e lógica também devem vir do conteúdo efetivamente recuperado pelo GitHub.

O catálogo atual não contém esse título. A implementação registra explicitamente sua ausência, em vez de criar um instrumento artificial ou modificar qualquer instrumento existente.

## 4. Cardinalidade aberta

A arquitetura não está limitada a três instrumentos.

Ela admite:

**coordenador + instrumento fixo + zero, um ou tantos instrumentos adicionais quantos forem indicados por títulos fornecidos pelo usuário.**

Não há limite máximo predefinido.

A inexistência de instrumentos adicionais não invalida a arquitetura. Quando houver adicionais, todos os títulos reconhecidos devem ser representados. Não pode haver redução arbitrária, truncamento, seleção por quantidade, substituição ou omissão.

Repetições do mesmo título não criam identidades duplicadas: geram ocorrências adicionais da mesma unidade, mantendo a contagem de ocorrências.

## 5. Recuperação pelo GitHub

O GitHub é a fonte de recuperação do conteúdo efetivo.

O conector não cria nem reconstrói a lógica operacional. Ele localiza e disponibiliza o que já está armazenado.

A política é:

**título identifica → GitHub localiza → conteúdo é recuperado → identidade é confirmada pelo conteúdo → aplicação é coordenada.**

O próprio coordenador deve ser recuperado pelo seu título quando presente. Cada adicional deve ser recuperado individualmente. O instrumento fixo deve ser recuperado pelo seu título previsto quando presente.

O conteúdo recuperado é base operacional, não texto que deva ser reproduzido integralmente na resposta final.

## 6. Separação entre instrumento e aplicação

Pertencem ao instrumento: identidade, finalidade, função, instruções essenciais e lógica operacional.

Pertencem à aplicação: demanda, contexto, escopo, parâmetros, critérios, formato, restrições, origem, destino, circunstâncias e adaptação.

Essa separação permite reutilização sem reconstrução integral do instrumento.

A mesma lógica pode ser aplicada a demandas diferentes sem alterar a identidade do instrumento.

## 7. Contextualização

A contextualização relaciona a lógica recuperada às circunstâncias concretas, considerando informações da conversa, objetivo, requisitos, restrições, dados, circunstâncias, dependências e condições da tarefa.

Contexto não é instrução própria do instrumento e não pode ser confundido com sua identidade.

## 8. Parametrização

A parametrização determina valores e condições variáveis da aplicação, incluindo escopo, parâmetros, critérios, formato, restrições, origem, destino, participantes, dependências e condições de validação.

Parâmetros podem ser fornecidos pelo usuário, determinados pelo contexto quando seguro ou definidos pela natureza da tarefa.

Parametrizar não autoriza alterar arbitrariamente finalidade ou lógica operacional.

## 9. Adaptação

A adaptação pode complementar, especificar, delimitar ou reorganizar aspectos dependentes do contexto.

Não pode substituir a lógica, descaracterizar finalidade, apagar identidade, inventar instruções ou transferir responsabilidade especializada sem fundamento.

A coordenação pode compatibilizar instruções, preservando, tanto quanto possível, finalidade e lógica de cada unidade.

## 10. Coordenação sem fusão

A coordenação é uma relação, não uma fusão.

O coordenador orienta, articula, organiza sequência, relaciona instruções, determina contexto/parâmetros, acompanha origem/destino, preserva responsabilidades e valida integridade.

Cada instrumento especializado continua responsável por sua própria lógica.

O resultado é aplicação conjunta, não transformação de vários instrumentos em um instrumento indistinto.

## 11. Uma única demanda concreta

Os instrumentos coordenados são aplicados sobre uma demanda concreta apresentada pelo usuário.

A demanda não se torna uma nova identidade de qualquer instrumento.

A sequência conceitual completa é:

**próprio título → própria ativação → títulos adicionais → ativação dos adicionais → título do instrumento fixo → ativação do fixo → recuperação individual pelo GitHub → preservação das identidades → interpretação conjunta → relação entre instruções → contextualização → parametrização → adaptação → aplicação conjunta → execução → validação → resultado.**

## 12. Origem e destino

Origem e destino são parâmetros operacionais, não propriedades permanentes da identidade do instrumento.

A localização física de um instrumento não determina automaticamente onde seu resultado deve ser produzido.

A arquitetura admite operação multidiretório: instrumentos podem ser recuperados de um diretório; resultados podem ser materializados em outro; auxiliares podem estar em outros diretórios; origem e destino podem ser diferentes.

A implementação registra origem explicitamente indicada e resolve destino de forma conservadora.

### Prioridade de destino

1. indicação explícita;
2. contexto inequivocamente determinante;
3. função original, quando realmente aplicável;
4. inferência contextual segura.

Associação temática fraca nunca é suficiente.

Sem determinação segura do destino, a camada de materialização não deve escrever.

## 13. Regra especial para Nocturna

**Nocturna não é destino padrão.**

Ela somente é destino quando explicitamente indicada ou inequivocamente determinada.

Outro destino explícito prevalece.

Na ausência de determinação suficiente, a materialização é suspensa.

## 14. Resultados intermediários

Resultados intermediários podem ser produzidos quando necessários.

Cada resultado intermediário deve conservar origem, instrumento responsável, etapa, destino e relação com o resultado final.

Isso permite integração sem perda de rastreabilidade.

## 15. Coordenação de escrita

Quando mais de um instrumento produzir conteúdo, o coordenador define responsabilidades, cada instrumento mantém sua lógica, resultados são integrados sem duplicação desnecessária e conflitos não são resolvidos apagando arbitrariamente uma instrução.

Decisões destrutivas exigem preservação das regras originais e validação de integridade.

Determinação de destino não transfere automaticamente funções.

## 16. Rastreabilidade

A arquitetura exige rastreabilidade ponta a ponta.

Os elementos mínimos são:

- título;
- instrumento;
- papel;
- ativação;
- recuperação;
- origem;
- destino;
- etapa;
- instrumento responsável;
- relação com resultado;
- validação.

A rastreabilidade liga a ocorrência original à unidade recuperada, à etapa de coordenação e ao resultado.

## 17. Validação final coordenada

Antes de considerar uma operação coordenada íntegra, devem ser verificadas:

1. instrumentos recuperados;
2. identidades corretas;
3. sequência;
4. responsabilidades;
5. origem;
6. destino;
7. resultados intermediários;
8. materialização final;
9. referências;
10. relações;
11. integridade de ponta a ponta.

A validação não substitui execução. Ela determina se a cadeia está estruturalmente íntegra.

## 18. Não reprodução integral

O conteúdo recuperado serve como base operacional.

Não é necessário reproduzir integralmente os instrumentos na resposta final quando isso não for necessário para execução.

O resultado final deve refletir a aplicação coordenada, preservando as distinções entre os participantes.

## 19. Fluxo multidiretório estendido

A arquitetura admite a extensão:

**TÍTULO → RECUPERAÇÃO → INSTRUMENTO → DEMANDA → CONTEXTO → ORIGEM → DESTINO → PARÂMETROS → ADAPTAÇÃO → EXECUÇÃO → VALIDAÇÃO → RASTREABILIDADE.**

Origem e destino são parâmetros da operação.

## 20. Garantias de não alteração

Esta complementação não altera conteúdo de instrumentos, não cria o instrumento fixo ausente, não presume identidade de adicionais, não limita quantidade de adicionais, não funde instrumentos, não transforma contexto em instrução, não transforma parâmetro em identidade, não transforma adaptação em substituição da lógica, não usa Nocturna como destino padrão, não autoriza escrita por associação temática e não reduz múltiplas ocorrências/títulos a uma unidade.

Ela acrescenta uma camada estruturada de relação, recuperação, coordenação, origem/destino e rastreabilidade sobre a correferência existente.

## 21. Modelo operacional

**título + requisição personalizada → correferência → identificação → acionamento → recuperação GitHub → confirmação pelo conteúdo → preservação da identidade → coordenação → contextualização → parametrização → adaptação → aplicação especializada → resultados intermediários → composição → destino → validação → rastreabilidade → resultado.**

A lógica permanece como eixo. A aplicação ajusta-se ao momento.

## 22. Relação com a implementação

A implementação mantém os campos existentes de `validate()` e adiciona `coordination`, sem remover os elementos estruturais atuais.

A nova seção inclui participante coordenador, participante fixo, coleção aberta de adicionais, cardinalidade não limitada, recuperação GitHub, demanda, contexto, parâmetros, origem, destino, adaptação, coordenação sem fusão, sequência, operação multidiretório, Nocturna, resultados intermediários, rastreabilidade, validação final e política de saída.

O `execution_plan` existente continua preservado. O pacote de execução carrega também metadados de coordenação, origem, destino, sequência e rastreabilidade.

## 23. Limite honesto da automação

A correferência automática identifica e classifica títulos. A camada complementar organiza coordenação e recuperação.

GitHub Actions pode validar, recuperar e materializar um pacote.

A aplicação efetiva das instruções recuperadas sobre a demanda continua sendo responsabilidade do runtime/agente que consome esse pacote. Nenhum campo `active`, `execution_plan` ou `resolved` deve ser interpretado como prova de execução externa já realizada.

Essa separação mantém a arquitetura verificável e impede que identificação seja confundida com execução real.

## 24. Contrato arquitetural completo e interconectado

Esta seção consolida os elementos estruturais dos dois textos de especificação em uma única relação, sem substituir a correferência existente e sem exigir a reprodução integral dos instrumentos.

### 24.1 Elementos permanentes e elementos variáveis

A arquitetura completa compreende:

- título;
- requisição personalizada;
- ChatGPT;
- conector GitHub;
- repositório;
- instrumento;
- instruções estruturadas;
- lógica operacional;
- demanda;
- contexto;
- contextualização;
- parametrização;
- adaptação;
- execução;
- origem;
- destino;
- participantes;
- dependências;
- resultados intermediários;
- composição;
- validação;
- rastreabilidade.

Pertencem ao instrumento, como núcleo estável: identidade, finalidade, função, instruções essenciais e lógica operacional. Pertencem à aplicação, como configuração variável: demanda, objetivo, requisitos, restrições, contexto, escopo, parâmetros, critérios, formato, origem, destino, circunstâncias, dependências e adaptações.

A estabilidade não exige que todos os aspectos da execução sejam invariáveis. Ela exige preservação daquilo que caracteriza finalidade, função e identidade operacional.

### 24.2 Unidade de acionamento

O título é referência nominal, identificador operacional, ponto de entrada, chave de acesso e mecanismo de acionamento. Ele não é apenas etiqueta e não precisa ser apresentado isoladamente.

A unidade de acionamento é:

**título + requisição personalizada no ChatGPT.**

O título determina qual instrumento deve ser localizado; a requisição determina a situação concreta na qual a lógica será instanciada. A escrita conjunta dessas duas partes liga estrutura estável e demanda variável.

### 24.3 Recuperação e fonte de verdade

O repositório conserva lógicas operacionais previamente estabelecidas. Ele não recria a lógica a cada demanda.

O conector GitHub localiza e disponibiliza o conteúdo existente; não cria, reconstrói ou presume a lógica. A identidade de um instrumento adicional só é confirmada pelo conteúdo efetivamente recuperado.

A cadeia de recuperação é:

**título → GitHub → localização → conteúdo efetivo → confirmação de identidade → instruções/lógica → aplicação.**

A ausência de um instrumento previsto deve ser registrada como ausência, e não compensada por conteúdo inventado.

### 24.4 Reutilização sem reconstrução

Reutilizar não significa repetir mecanicamente. O mesmo instrumento pode receber diferentes demandas porque a lógica permanece como eixo e a aplicação pode variar.

O repositório preserva aquilo que deve permanecer e permite aquilo que precisa mudar. Não é necessário reconstruir, reformular ou reproduzir integralmente um instrumento para cada aplicação.

A identidade decorre da continuidade de lógica, finalidade e função, e não da repetição literal de palavras.

### 24.5 Contextualização, parametrização e adaptação

A contextualização relaciona lógica e circunstâncias da conversa.

A parametrização determina valores e condições variáveis, podendo incluir escopo, parâmetros, critérios, formato, restrições, origem, destino, participantes, dependências e condições de validação.

A adaptação complementa, especifica, delimita ou reorganiza aspectos dependentes da situação. Ela permanece subordinada à lógica, finalidade e função do instrumento e não pode inventar instruções, substituir a lógica ou transferir responsabilidade especializada.

### 24.6 Coordenação

**Acionamento Coordenado de Instrumentos Promptuais** é o instrumento coordenador arquiteturalmente previsto.

Ele orienta, coordena e articula. Não substitui os instrumentos especializados.

A arquitetura coordenada é:

**coordenador + instrumento fixo “Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas” + zero, um ou tantos instrumentos adicionais quantos forem indicados por títulos do usuário.**

O instrumento fixo permanece uma unidade própria. Cada adicional permanece uma unidade própria. O coordenador estabelece relações entre essas unidades, sem absorção, fusão, descaracterização ou substituição.

### 24.7 Cardinalidade aberta

Não existe limite máximo predefinido para instrumentos adicionais.

Cada título adicional é uma unidade própria que deve ser:

1. reconhecida;
2. localizada individualmente;
3. recuperada;
4. compreendida pelo conteúdo efetivo;
5. preservada como unidade;
6. incorporada à coordenação;
7. mantida distinguível das demais.

Repetições são ocorrências adicionais da mesma unidade, não novas identidades.

Nenhum adicional pode ser omitido por quantidade, truncado, substituído ou selecionado arbitrariamente.

A inexistência de adicionais não invalida a arquitetura: permanecem o coordenador e o instrumento fixo.

### 24.8 Uma demanda concreta e responsabilidades

A aplicação conjunta incide sobre uma única demanda concreta do usuário.

O coordenador articula as instruções; cada instrumento especializado executa sua própria lógica; contexto, parâmetros e adaptação pertencem à aplicação; e o resultado representa a combinação coordenada.

A coordenação não transforma a demanda em identidade de nenhum instrumento.

### 24.9 Origem, destino e multidiretório

Origem e destino são parâmetros operacionais.

O local físico do instrumento não determina automaticamente o local do resultado. Instrumento, auxiliares, origem, arquivos afetados e destino podem estar em diretórios diferentes.

A resolução do destino obedece à prioridade:

**indicação explícita → contexto inequivocamente determinante → função original quando realmente aplicável → inferência contextual segura.**

Associação temática fraca nunca autoriza escrita.

### 24.10 Nocturna

Nocturna é destino especial, nunca padrão.

Somente indicação explícita ou determinação inequívoca autoriza seu uso. Outro destino explicitamente indicado prevalece. Em ambiguidade, não se materializa conteúdo dependente dessa decisão.

Essa regra é uma regra de destino operacional e não altera a identidade ou a lógica de qualquer instrumento.

### 24.11 Resultados intermediários e composição

Resultados intermediários podem ser produzidos quando necessários.

Cada resultado deve manter:

- origem;
- instrumento responsável;
- etapa;
- destino;
- relação com o resultado final.

Quando múltiplos instrumentos produzem conteúdo, o coordenador define responsabilidades e integração, evitando duplicação desnecessária. Conflitos devem preservar as regras originais; decisões destrutivas exigem validação de integridade.

Determinar destino não transfere função especializada.

### 24.12 Fluxos complementares

O fluxo fundamental permanece preservado:

**título → identificação/acionamento → requisição → localização GitHub → recuperação → instruções/lógica → demanda → contexto → contextualização → parametrização → adaptação → aplicação → execução → resultado.**

O fluxo coordenado amplia-o para:

**próprio título → própria ativação → títulos adicionais → ativações adicionais → título fixo → ativação fixa → recuperação individual → preservação das identidades → interpretação conjunta → relação entre instruções → contextualização → parametrização → adaptação → aplicação conjunta → execução → validação → resultado.**

O fluxo multidiretório acrescenta:

**TÍTULO → RECUPERAÇÃO → INSTRUMENTO → DEMANDA → CONTEXTO → ORIGEM → DESTINO → PARÂMETROS → ADAPTAÇÃO → EXECUÇÃO → VALIDAÇÃO → RASTREABILIDADE.**

Esses fluxos são complementares, não substitutivos.

### 24.13 Rastreabilidade ponta a ponta

Toda operação coordenada deve poder relacionar:

**título → instrumento → papel → ativação → recuperação → origem → destino → etapa → responsável → resultado → validação.**

A rastreabilidade deve acompanhar tanto a ocorrência original quanto os resultados intermediários e o resultado final.

### 24.14 Validação final

A validação final coordenada confirma, no mínimo:

1. instrumentos recuperados;
2. identidades corretas;
3. sequência;
4. responsabilidades;
5. origem;
6. destino;
7. resultados intermediários;
8. materialização final;
9. referências;
10. relações;
11. integridade de ponta a ponta.

Validação estrutural não é prova de execução externa.

### 24.15 Política de saída e limite honesto

O conteúdo recuperado é base operacional. Não precisa ser reproduzido integralmente ao usuário quando isso não for necessário.

matches, active_instruments, execution_plan, participantes resolvidos ou qualquer estado equivalente representam identificação, planejamento ou recuperação; não constituem, isoladamente, prova de que um agente externo executou as instruções.

A execução efetiva continua pertencendo ao runtime que consome a estrutura recuperada.

### 24.16 Garantias de preservação

A complementação:

- preserva a correferência atual;
- preserva múltiplas ocorrências e múltiplos títulos;
- preserva o catálogo e a árvore física;
- preserva a distinção entre instrumento e aplicação;
- preserva identidade, finalidade, função, instruções e lógica;
- preserva a separação entre coordenador e especialistas;
- mantém cardinalidade adicional aberta;
- permite operação multidiretório;
- mantém origem e destino como parâmetros;
- mantém Nocturna fora da condição de destino padrão;
- permite resultados intermediários rastreáveis;
- exige validação final;
- evita reprodução integral desnecessária;
- não cria conteúdo para instrumento ausente;
- não presume identidade pelo título sozinho;
- não funde instrumentos;
- não transforma contexto, parâmetro ou adaptação em identidade;
- não autoriza escrita por associação temática;
- não transfere responsabilidades especializadas por mera determinação de destino.

A complementação, portanto, melhora o funcionamento da correferência por títulos acrescentando uma camada operacional interconectada, sem apagar ou substituir sua estrutura atual.
