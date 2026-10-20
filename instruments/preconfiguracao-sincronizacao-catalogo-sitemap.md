# PRÉCONFIGURAÇÃO DE SINCRONIZAÇÃO, CORREFERÊNCIA E VALIDAÇÃO AUTOMÁTICA DA PROMPTÁRIA

## 1. Finalidade e compatibilidade estrutural

Este instrumento estabelece uma pré-configuração reutilizável para demandas futuras de manutenção do catálogo, navegação e automação. Deve coexistir com os instrumentos, resolvedor, executor, contratos JSON, testes e workflows já vigentes no repositório. Não autoriza substituir estruturas existentes por uma arquitetura presumida.

## 2. Modelo de referência fornecido

O modelo de sincronização apresentado para a árvore `Promptária/` define estes elementos estruturais, que devem ser preservados quando essa árvore e os arquivos correspondentes realmente existirem:

- raiz do projeto, diretório `Promptária`, `manifest.json` e `sitemap.xml`;
- validação de `schema_version === "2.0"` e de `manifest.instruments`;
- descoberta de diretórios que contenham `Index.html`;
- indexação por caminho e cálculo do maior identificador numérico;
- extração de título de `h1`, com fallback para `title` e nome do diretório;
- inserção antes da âncora `Promptária/Adaptacao-e-Execucao-Extensiva-Multidiretorio/Index.html`, com encadeamento `previous`/`next`;
- preservação dos instrumentos existentes e correção de elos navegacionais ausentes;
- correção da colisão histórica de ID descrita no modelo e de IDs duplicados;
- injeção de `navegacao-neural.js` nos documentos HTML aplicáveis;
- sincronização de `entry` e `canonical_reference`;
- geração do sitemap a partir da base `https://outocarlos003-lang.github.io/Prompt-ria/`;
- gravação apenas quando o conteúdo calculado difere do conteúdo existente.

O código de referência é específico à estrutura acima. A árvore atualmente documentada neste repositório usa `instruments/*.md`, um resolvedor Python, um executor separado e artefatos de auditoria. Portanto, não se deve executar cegamente o código de referência nem criar um `manifest.json` paralelo como se fosse a fonte canônica: isso criaria dois catálogos concorrentes.

## 3. Pré-configuração para demandas futuras

Para toda demanda transmitida pelos pontos de entrada autorizados da Promptária:

1. Ler a solicitação completa antes de alterar arquivos.
2. Recuperar todos os instrumentos cujos títulos canônicos estejam mencionados; preservar correspondências múltiplas e o conteúdo integral.
3. Incluir os três componentes-base definidos pelo resolvedor vigente: arquitetura coordenadora, protocolo-mestre e instrumento operacional do GitHub.
4. Tratar a menção genérica como acionamento da função própria do instrumento; uma função diferente só pode ser aplicada quando a atribuição for explícita e inequívoca.
5. Verificar a estrutura real do repositório e identificar a fonte canônica antes de escolher os arquivos a alterar.
6. Preservar nomes, IDs estabilizados, campos, caminhos, elos navegacionais, permissões, contratos, testes e mecanismos de auditoria existentes, exceto quando a solicitação autorizar explicitamente uma mudança específica.
7. Aplicar mudanças de forma idempotente: uma segunda execução sem alterações de entrada não deve produzir diferenças artificiais.
8. Validar o schema antes de escrever; detectar IDs duplicados, caminhos duplicados, destinos ausentes, referências quebradas e componentes obrigatórios ausentes.
9. Gerar ou atualizar o sitemap somente se o projeto realmente mantiver esse artefato e sua URL-base estiver confirmada na configuração existente.
10. Executar testes e validações após a mudança. Distinguir plano, alteração gravada, validação concluída e publicação; nunca declarar uma etapa não observada como executada.

## 4. Segurança e falha fechada

A identificação e a recuperação de instrumentos não equivalem à execução de suas instruções. O resolvedor vigente continua sendo planejamento; o executor permanece separado. A escrita real exige as autorizações explícitas previstas no executor e não pode ser habilitada por este instrumento nem pelo workflow de resolução. Em caso de incompatibilidade de schema, âncora inexistente, fonte canônica ambígua, destino inseguro ou teste falho, interromper a mutação e registrar a causa.

## 5. Critério de conclusão

A tarefa só pode ser considerada validada quando houver evidência de: (a) preservação das estruturas anteriores; (b) integração de todos os instrumentos aplicáveis; (c) ausência de colisões de identidade; (d) referências e navegação coerentes; (e) artefatos derivados sincronizados, quando aplicáveis; (f) testes concluídos; e (g) relatório que diferencie mudanças realizadas de itens não aplicáveis ou pendentes.


## 6. Arquitetura operacional unificada de integridade

Princípio obrigatório: tudo se conecta, tudo se rastreia e tudo se integra. Nenhum conteúdo deve ser considerado preservado, integrado, funcional ou concluído sem localização coerente, relação verificável, procedência compreensível, destino legítimo e validação proporcional às evidências disponíveis.

Unifique rastreabilidade navegacional, integridade sistêmica e rastreabilidade de produção numa única arquitetura operacional. São dimensões distintas e interdependentes: navegar localiza; integrar estabelece relações; produzir transforma; validar comprova. Nenhuma dimensão substitui as demais e nenhuma poderá declarar sucesso isoladamente.

Mantenha três redes complementares e mutuamente verificáveis:

- **Rede navegacional:** página inicial, pesquisa, botões, páginas, pastas, subpastas, links, retornos, ramificações e caminhos de acesso.
- **Rede funcional:** arquivos, diretórios, módulos, componentes, dados, assets, configurações, scripts, workflows, APIs, serviços, dependências e contratos.
- **Rede de produção:** origem, instrumentos, participantes, operações, transformações, artefatos intermediários e finais, referências, consumidores, destinos e resultados.

A página inicial deverá convergir e distribuir o acesso; a navegação deverá revelar os conteúdos; a integridade deverá comprovar as relações; e a produção deverá explicar a obtenção e a destinação dos resultados. Nenhuma rede pode operar isoladamente, contradizer as outras ou ocultar relações indispensáveis.

## 7. Protocolo de rastreio do repositório e do site

Quando houver site fornecido e repositório GitHub associado, acessível e autorizado, inspecione a estrutura real antes de agir. Identifique arquivos, diretórios, rotas, dependências, contratos, configurações, mecanismos de carregamento, build, testes e publicação. Diferencie fatos comprovados, inferências justificadas e relações ainda não verificadas; não presuma recursos que não foram encontrados.

Edite ou reorganize o site somente com acesso e autorização efetivos. Preserve conteúdo, identidade, finalidade, funcionalidades, contratos válidos e organização original, acrescentando conexões sem destruir a estrutura preexistente. A árvore física organiza; a rede navegacional conecta; a pesquisa aproxima; a navegação revela; o retorno preserva a continuidade.

A página inicial deverá encaminhar às áreas relevantes, estas às subseções e as subseções às páginas e recursos específicos. A pesquisa deverá atravessar níveis legitimamente indexáveis. Cada resultado deve apontar para o recurso correspondente e, quando pertinente, apresentar localização, contexto e relações. Não exponha arquivos privados, segredos ou recursos restritos. Para conteúdo dinâmico ou não indexável, declare a limitação sem simular capacidade inexistente.

Todo botão acionável deverá ter propósito inequívoco, destino válido e comportamento verificável. Trate indisponibilidade, falhas, permissões e dependências; preserve parâmetros, estados, avanço, retorno e ramificações necessários à continuidade. Mantenha rótulos compreensíveis, foco acessível e dimensões de interação adequadas. Não mantenha controles inertes, links quebrados ou destinos sem orientação.

Preserve toda informação existente relevante. Quando os materiais permitirem, compare estados anterior e posterior e registre conteúdo preservado, alterado, movido, criado ou removido. Cada conteúdo relevante deverá ter caminho de acesso, descoberta compatível e referências coerentes, respeitados os limites legítimos de acesso.

## 8. Dupla camada de rastreabilidade e identidade

Mantenha simultaneamente:
1. **Rastreabilidade navegacional:** onde o conteúdo está, como é descoberto, por quais caminhos é alcançado e para quais recursos pode prosseguir.
2. **Rastreabilidade de produção:** de onde veio, qual instrumento o processou, quais operações e recursos participaram, onde o resultado foi armazenado e como sua integridade pode ser verificada.

Vincule as camadas: localização correta não prova produção legítima, e produção rastreável não garante navegabilidade. Diferencie identidade do conteúdo de localização física. Mover um arquivo não muda necessariamente sua identidade; conservar o caminho não prova que o conteúdo permaneceu igual; cópias semelhantes podem ter procedências diferentes. Use identificadores, versões, hashes ou mecanismos equivalentes quando disponíveis e adequados.

Quando um artefato for movido, atualizado ou substituído, atualize referências navegacionais e preserve histórico necessário. Se o conteúdo mudar sem mudança de caminho, registre versão ou estado conforme os mecanismos existentes.

A cadeia de produção a preservar é:

**CONTEÚDO ORIGINAL → INSTRUMENTO RESPONSÁVEL → INSTRUMENTOS PARTICIPANTES → OPERAÇÃO → ORIGEM → TRANSFORMAÇÃO → ARQUIVO/ARTEFATO → DESTINO → REFERÊNCIAS → VALIDAÇÃO → RESULTADO.**

Vincule cada etapa à anterior e à seguinte quando aplicável. Preserve entradas, operações, saídas intermediárias, múltiplas saídas e contribuições convergentes sem apagar procedência. Se não houver arquivo físico, registre o resultado lógico ou operacional pertinente sem inventar artefatos. Nenhum resultado poderá perder o vínculo com a demanda e o processo que o originaram.

## 9. Origem, ambiente de execução e destino

Diferencie rigorosamente:
- **Origem:** de onde o conteúdo foi obtido.
- **Ambiente de execução:** onde a operação ocorreu.
- **Destino:** onde o resultado deve ser encaminhado.

Não deduza o destino a partir da localização do executor ou do arquivo de instrução. Antes do encaminhamento, verifique determinação do destino, compatibilidade, permissões, convenções, consumidores e referências dependentes. Registre caminhos anteriores e posteriores, artefatos criados, editados, preservados ou legitimamente removidos e instrumentos auxiliares quando aplicável.

Destino determinado, encaminhamento executado e encaminhamento validado são estados distintos. A determinação não comprova execução; a presença de arquivo não comprova integração; caminho acessível não comprova adequação semântica nem reconhecimento pelo build. Se o destino for ambíguo ou não estiver suficientemente determinado, solicite esclarecimento antes de uma operação dependente dessa decisão.

**Nocturna** somente poderá ser destino quando explicitamente indicada ou inequivocamente determinada. Nunca a estabeleça por inferência fraca. Quando determinada legitimamente, valide caminho, permissões, estrutura, referências, consumidores e integridade da cadeia. Se não for possível confirmar a chegada, registre a limitação e não declare o encaminhamento concluído.

A pasta ou diretório `instruments/` da Promptária não se confunde com o diretório de saída. Registre separadamente instrumento executor, localização do instrumento, artefato produzido e destino específico. Antes de substituir ou reorganizar instrumento, examine consumidores, títulos canônicos, convenções de descoberta, referências cruzadas e processos de execução. Após a alteração, valide identificação, localização, descoberta e funcionamento dos consumidores.

## 10. Integridade sistêmica e dependências

Trate o repositório como uma arquitetura funcional única. A unidade de correção é o sistema, mesmo quando a alteração se limita a um recurso. A existência física não prova integração: arquivos podem estar inacessíveis, módulos podem violar contratos, páginas podem aparecer sem cumprir sua finalidade e operações podem produzir resultados incompatíveis com consumidores.

Antes de alterar, identifique função, consumidores, provedores, caminhos de carregamento e efeitos diretos e indiretos. Examine relações estáticas, dinâmicas, externas, convencionais e descobertas automaticamente. Ausência de referência textual não prova ausência de dependência; nomes semelhantes não provam compatibilidade.

Verifique conforme aplicável:

- HTML ↔ CSS e JavaScript;
- JavaScript ↔ módulos, scripts e bibliotecas;
- páginas ↔ rotas e componentes;
- componentes ↔ estilos, scripts e dados;
- imagens, fontes, ícones e assets ↔ consumidores;
- manifest ↔ aplicação e sitemap ↔ páginas reais;
- formulários ↔ processadores;
- frontend ↔ APIs, backend, Workers e serviços externos;
- scripts ↔ arquivos gerados ou consumidos;
- workflows ↔ arquivos, comandos e permissões reais;
- build/deploy ↔ estrutura efetiva;
- imports, exports, IDs, endpoints, parâmetros e caminhos ↔ destinos correspondentes;
- fallbacks e tratamento de erros ↔ fluxos reais.

Verifique existência, resolução, contratos e comportamento esperado. Rastreie dependências nos dois sentidos: o que cada recurso utiliza, quem o utiliza e quais funcionalidades podem ser afetadas. Considere defeito também incorreção, desatualização, incompatibilidade ou ruptura de relação.

Preserve arquitetura válida e contratos existentes. Não mascare falhas removendo funcionalidades, neutralizando erros ou substituindo fluxos por atalhos. Consolide duplicações somente após verificar consumidores, contratos, contextos, fallbacks e dependências. Não confunda semelhança com redundância, nem ausência de ligação explícita com inutilidade. Considere carregamento dinâmico, convenções, descoberta automática, build, deploy e integração externa.

Antes de remover, mover, renomear, substituir ou fundir, rastreie consumidores diretos e indiretos, imports, exports, rotas, scripts, workflows, configurações e processos de build/deploy. Se o impacto não puder ser determinado com segurança, evite remoção irreversível e registre a incerteza. Após alterações, atualize caminhos relativos e absolutos, HTML, CSS, JavaScript, aliases, manifests, sitemaps, configurações, comandos, workflows, documentação operacional e mecanismos de descoberta pertinentes.

Organize por responsabilidade, não por aparência. Agrupe responsabilidades relacionadas quando isso melhorar manutenção, descoberta e reutilização, mantendo separações justificadas por contexto, segurança, ambiente ou ciclo de vida. Evite abstração excessiva, novas dependências desnecessárias e movimentações cosméticas arriscadas. Quando organização e funcionamento entrarem em conflito, preserve o funcionamento válido e reorganize de forma controlada.

## 11. Operações coordenadas entre instrumentos

Para operações com múltiplos instrumentos, registre coordenador, participantes, ordem de execução, responsabilidades, resultados intermediários, composição, destino final e validações. Preserve procedência de cada contribuição e verifique compatibilidade de entradas e saídas, formatos, parâmetros, caminhos e contratos.

Em etapas sequenciais, confirme a ordem; em operações paralelas, verifique sincronização e pontos de convergência. Não considere a operação concluída apenas porque cada instrumento produziu uma saída: valide interfaces, composição e encaminhamento final. O resultado composto não deve apagar contribuições individuais; estas não devem impedir validação do conjunto.

Diante de incompatibilidade, identifique a divergência, corrija a relação afetada e repita verificações pertinentes. Registre falhas, tentativas relevantes, correções e resultados conforme evidência, sem atribuir ações não executadas. Se uma contribuição for descartada, transformada ou substituída, registre a razão e distinga o resultado originalmente produzido daquele efetivamente incorporado.

## 12. Verificações antes, durante e depois

- **Antes:** leia a demanda completa; identifique instrumentos e títulos; confirme origem, finalidade, autorização, destino, dependências, contratos, riscos e estado real dos arquivos; estabeleça critérios de aceitação e plano reversível proporcional ao risco.
- **Durante:** acompanhe operações, mudanças, permissões, entradas e saídas; registre resultados intermediários e rupturas; mantenha a ligação entre demanda, instrumentos, arquivos e decisões.
- **Depois:** confirme conteúdo, destino, referências, consumidores, navegação, integridade, ausência de órfãos e continuidade dos fluxos; execute testes aplicáveis; compare estados anterior e posterior quando possível.

A conclusão deverá ser classificada com precisão como **verificada**, **inferida com justificativa**, **não verificada** ou **falha**. Diferencie plano, recuperação de conteúdo, tentativa, execução confirmada e resultado validado. Testes recomendados não são testes executados. Se uma relação não puder ser comprovada, registre a lacuna, delimite o impacto e não apresente presunção como fato.

## 13. Critérios de falha, recuperação e conclusão

Considere incompleta uma operação com destino incorreto, referência quebrada, conteúdo ou contexto perdido, artefato incompatível, consumidor desconectado, relação rompida ou procedência insuficiente. Classifique falhas como estruturais, navegacionais, funcionais, de produção, de integração ou de validação. Identifique relação afetada, elementos envolvidos, impacto e dependências a reexaminar.

Corrija a causa quando houver evidência, autorização e condições seguras; repita os testes pertinentes. Se não for possível corrigir ou validar, registre o que está funcional, pendente ou não verificável. Um resultado plausível não comprova procedência; arquivo presente não comprova compatibilidade; execução encerrada não comprova funcionamento.

Use esta sequência de validação final:

**origem correta? → conteúdo correto? → transformação correta? → destino correto? → referências corretas? → consumidores conectados? → arquitetura preservada? → resultado íntegro? → rastreabilidade preservada?**

Cada resposta exige evidência compatível com o projeto. Compare estados anteriores e posteriores quando possível e examine artefatos criados, editados, movidos, preservados ou removidos, referências afetadas, contratos, mecanismos de descoberta, registros de produção e resultados intermediários.

## 14. Ordem operacional obrigatória para demandas futuras

Execute nesta ordem, adaptando apenas quando a natureza da demanda justificar e registrando a razão:

**entender o sistema → rastrear relações → identificar falhas e redundâncias → corrigir conexões → consolidar com segurança → reorganizar a estrutura → atualizar referências → validar dependências → testar fluxos de ponta a ponta → registrar evidências e limitações → declarar a conclusão proporcionalmente ao que foi comprovado.**

A pré-configuração deve ser aplicada desde a primeira solicitação, por correspondência com títulos canônicos e inclusão automática deste instrumento nos planos do resolvedor vigente. Preserve todos os campos de demandas estruturadas, inclusive campos desconhecidos ou futuros; não descarte estrutura JSON nem transforme dados históricos em estado atual sem verificação. A menção ou recuperação de um instrumento não significa que seu conteúdo foi executado.

Mantenha o padrão seguro atual: simulação por padrão, executor separado, permissões mínimas, destino explícito, validação de caminhos, autorização efetiva para escrita e auditoria. Este instrumento não amplia permissões nem altera por si só workflows, contratos, executor ou políticas de acesso. Qualquer mudança de código ou configuração deve ser implementada e testada separadamente, com referências e evidências verificáveis.

**Regra unificada:** todo conteúdo deverá ser encontrável; todo caminho deverá resolver seu destino; todo destino deverá permitir continuidade ou retorno coerente; toda relação deverá corresponder a conexão verificável; toda transformação deverá preservar procedência; toda reorganização deverá restabelecer referências afetadas; e toda conclusão deverá decorrer de evidências. Preserve o conteúdo, mantenha a identidade, rastreie transformações, determine destinos, restabeleça conexões e valide resultados. A integridade resulta da correspondência entre todas as dimensões, nunca da aprovação isolada de uma delas.
