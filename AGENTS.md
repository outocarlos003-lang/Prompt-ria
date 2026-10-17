# Regras universais de execução para agentes

Estas regras são a configuração operacional comum do repositório. Devem ser lidas antes de executar qualquer tarefa aqui, independentemente do agente, interface ou ferramenta utilizada. Instruções específicas de plataforma complementam este arquivo; não o substituem nem podem ampliar o escopo do pedido do usuário.

O modelo genérico de coordenação, acionamento, recuperação, aplicação cumulativa e verificação dos instrumentos está especificado em instruments/protocolo-mestre-acionamento-automatico.md. Aplique-o em conjunto com estas regras universais e com os instrumentos integrais pertinentes; a referência documental não significa que ambientes externos que não carreguem estes arquivos sejam automaticamente configurados.

## Prioridade obrigatória

1. Pedido explícito atual.
2. Contexto ativo que o pedido claramente continua.
3. Regras e estrutura canônicas do repositório de destino.
4. Verificações diretamente necessárias para concluir o pedido.
5. Pendências independentes, que não devem desviar a execução.

Se houver conflito entre uma hipótese do agente e o pedido explícito, prevalece o pedido explícito, dentro das políticas de segurança e permissões disponíveis.

## Regra universal de acionamento e registro

Para toda mensagem que contenha uma demanda identificável — pergunta substantiva, instrução, tarefa, análise, revisão, proposta ou decisão — aplique este protocolo, independentemente do assunto. Não o aplique automaticamente a saudações ou mensagens casuais sem demanda própria.

1. Identifique o resultado solicitado, limites, destino e critério verificável de conclusão.
2. Acione os instrumentos coordenador e operacional do GitHub definidos no contexto da Promptária, quando estiverem disponíveis. Recupere suas instruções pertinentes antes da execução; títulos alternativos ou instrumentos especializados não dispensam este protocolo comum.
3. Procure registros existentes no repositório e nas issues acessíveis, usando título, objetivo e contexto. Se houver registro equivalente, atualize-o ou vincule-o; não crie duplicata.
4. Registre ou vincule a demanda no GitHub e recupere os registros pertinentes. O registro deve distinguir pedido, destino, estado, evidências e limitações.
5. Aplique a instrução especializada correta e execute a alteração concreta autorizada. Registro, pesquisa, plano ou proposta não substituem a execução solicitada.
6. Verifique o estado final com evidência observável e atualize o registro com o resultado.

## Equivalência dos instrumentos especializados

Todo instrumento promptual opcional explicitamente indicado ou identificado deve ser acionado para sua função específica e também obedecer às operações comuns de identificação, recuperação, registro, aplicação e verificação. Isso não apaga diferenças entre funções nem autoriza atribuir a um instrumento responsabilidades que não possui.

## Fluxo específico do site Nocturna

Quando o pedido solicitar, implicar inequivocamente ou determinar inserir, alterar, recuperar ou validar conteúdo na Nocturna, acione o fluxo editorial específico, independentemente do título do instrumento utilizado:

1. Identifique o repositório, o tipo de conteúdo e o destino canônico.
2. Verifique conteúdo equivalente no destino correto antes de criar ou alterar.
3. Execute a alteração autorizada no repositório de destino e siga o workflow aplicável.
4. Verifique separadamente arquivo gravado, workflow, deploy e página pública; não infira uma etapa a partir de outra.

Uma issue no GitHub não significa que o conteúdo foi inserido no site; uma proposta não significa publicação.

## Estados e transparência de conclusão

Para cada demanda, relate separadamente:

- **Identificada:** o objetivo e os limites foram reconhecidos.
- **Registrada/vinculada:** há registro GitHub novo ou referência verificável a registro equivalente.
- **Aplicada/executada:** a operação solicitada foi realmente realizada.
- **Verificada:** há evidência do estado final esperado.

Se uma etapa depender de acesso, autorização, informação ou capacidade indisponível, registre a limitação e não declare conclusão integral. Nunca afirme commit, workflow, deploy ou publicação pública sem evidência verificável.

## Trava de escopo

Antes de agir, identifique internamente: ação solicitada, destino, conteúdo/limites e critério verificável de conclusão. Mantenha esse objetivo como trava durante toda a execução.

Leia a mensagem completa. Não infira autorização para tarefas adicionais a partir do histórico, de problemas descobertos ou de preferências presumidas.

“Continue”, “@GitHub”, “próxima etapa” e expressões equivalentes mantêm o objetivo ativo; não autorizam trocar de tarefa.

Execute a alteração concreta solicitada. Pesquisa, auditoria, explicação, issue, comentário ou plano não substituem a entrega pedida.

Não modifique arquivos, serviços, workflows ou subsistemas não relacionados, salvo quando forem dependência causal comprovada do resultado ou forem explicitamente autorizados.

Não transforme falhas incidentais em bloqueios. Investigue dependência causal antes de interromper a tarefa.

Resolva detalhes rotineiros de baixo risco usando os padrões existentes. Pergunte apenas quando uma ambiguidade material impedir uma execução segura e correta.

Quando o pedido estiver concluído, verifique o resultado solicitado e encerre. Não invente uma próxima tarefa.

## Execução e recuperação

1. Inspecione somente o contexto, os arquivos e as ferramentas necessários.
2. Faça a alteração no destino solicitado, preservando conteúdo existente e evitando duplicatas.
3. Execute as verificações diretamente relacionadas ao critério de conclusão.
4. Relate separadamente o que foi alterado e o que foi realmente verificado. Nunca declare commit, workflow, deploy ou publicação pública sem evidência.

Se o usuário apontar um desvio, interrompa a trilha lateral, reconheça o erro, retome o objetivo original e corrija as regras de configuração pertinentes sem ampliar novamente o escopo.

## Compatibilidade entre ambientes e limite real

Este arquivo é uma instrução portável para agentes e ferramentas que leem AGENTS.md ou recebem seu conteúdo como contexto. Instruções específicas, como .github/copilot-instructions.md, devem apontar para ele e repetir os controles essenciais quando a plataforma não carregar arquivos AGENTS.md.

Nenhum arquivo dentro de um repositório consegue, por si só, impor comportamento automático a todo ambiente, modelo, conversa ou integração. A aplicação automática depende de a ferramenta carregar estas instruções, de permissões válidas e de seus próprios mecanismos de configuração. Automações agendadas não são gatilhos por mensagem e não garantem acionamento em cada conversa. Para cobertura efetiva, conecte este protocolo às instruções persistentes de cada ambiente utilizado e valide essa integração. Não prometa universalidade técnica onde ela não existe.

## Regra canônica: título aciona; prompt integral governa

Esta regra aplica-se a todos os instrumentos promptuais existentes e futuros, a qualquer título principal, título alternativo, subtítulo, nome abreviado, alias, rótulo de interface ou formulação equivalente. Não exige nem autoriza editar o conteúdo dos instrumentos promptuais existentes.

**Função exclusiva do título:** qualquer título reconhecido funciona como chave de identificação, busca, roteamento e acionamento do instrumento correspondente. O título não é, por si só, a instrução operacional.

**Recuperação obrigatória:** depois de identificar o instrumento pelo título, localize e leia seu prompt integral canônico, incluindo todas as etapas, restrições, condições, critérios, formatos de saída e instruções de verificação. Leia o arquivo ou bloco-fonte completo, não apenas o cabeçalho ou uma passagem selecionada.

**Fonte de autoridade:** conduza a execução a partir do prompt integral recuperado e das instruções universais deste AGENTS.md, respeitando a prioridade do pedido explícito atual. O resumo, a descrição, a prévia, a ementa, o título longo ou curto, o nome do arquivo, o texto do cartão e os metadados servem somente à descoberta e à navegação; nunca substituem nem resumem operacionalmente o prompt integral.

**Proibição de inferência pelo título:** não deduza etapas, métodos, parâmetros, permissões, critérios de conclusão ou resultados esperados a partir da semântica do título. Não execute uma versão reconstruída, abreviada ou presumida do instrumento quando seu texto integral estiver disponível.

**Resolução de aliases:** se qualquer título ou alias apontar para o mesmo instrumento, resolva-o para a mesma fonte integral canônica. Não trate títulos equivalentes como instrumentos distintos sem evidência documental.

**Integridade e ambiguidade:** se houver vários candidatos, compare seus registros e fontes integrais para determinar a correspondência. Se não for possível confirmar qual instrumento corresponde ao título, informe a ambiguidade e peça esclarecimento somente quando ela impedir uma execução correta. Se a fonte integral estiver inacessível ou incompleta, não improvise o conteúdo ausente: informe a limitação e prossiga apenas com as partes cuja autoridade esteja confirmada.

**Execução fiel:** após a recuperação, aplique o instrumento completo ao pedido real, adaptando apenas o que o próprio instrumento permitir e sem ultrapassar os limites explícitos do usuário. Preserve as instruções, os instrumentos e seus conteúdos existentes; esta regra altera o protocolo de descoberta e execução, não os prompts armazenados.

**Verificação rastreável:** antes de declarar o instrumento aplicado, confirme e registre, quando o fluxo de trabalho permitir, o título/alias acionador, a localização da fonte integral consultada e o resultado da aplicação. Diferencie claramente “título identificado”, “prompt integral recuperado”, “instrumento aplicado” e “resultado verificado”.

**Interface e cópia:** catálogos, cartões, resultados de pesquisa e visualizações podem exibir títulos e resumos para navegação, mas uma ação apresentada como “copiar prompt” ou equivalente deve copiar o prompt integral do instrumento, não apenas o resumo ou a prévia. Se a interface não consegue garantir isso, declare a limitação e não apresente a prévia como prompt completo.

**Limite de aplicação automática:** estas regras orientam agentes e ferramentas que efetivamente carregam este arquivo ou recebem seu conteúdo como instrução. Não alegue que o título, sozinho, consegue impor comportamento a qualquer modelo, conversa ou integração que não tenha acesso ao protocolo e à fonte integral.

**Invariante operacional:** título/alias → localizar instrumento → recuperar e ler prompt integral → executar conforme o prompt integral → verificar. Nenhuma operação pode usar o título ou seu resumo como substituto do instrumento promptual subjacente.

## Regra obrigatória de retorno integral dos instrumentos acionados

Para toda demanda identificável, além de recuperar e aplicar as instruções, retorne ao usuário o texto integral canônico de cada instrumento promptual efetivamente acionado. Esta regra vale para o instrumento coordenador fixo, o instrumento operacional fixo e todos os instrumentos especializados adicionais que tenham sido identificados como pertinentes — não apenas para Nocturna nem apenas para o instrumento nomeado com maior destaque na mensagem.

**Inventário antes da execução:** consulte o catálogo/manifesto da Promptária e identifique todos os instrumentos fixos e especializados que se aplicam à demanda. Não limite a busca ao nome mais evidente, ao instrumento opcional citado por último ou ao destino editorial.

**Fonte integral por instrumento:** para cada instrumento acionado, localize a fonte canônica e leia o conteúdo completo. Use o texto integral armazenado na Promptária/GitHub, nunca apenas título, alias, ementa, cartão, trecho de busca ou resumo.

**Retorno obrigatório:** inclua na resposta o texto integral de cada instrumento acionado, identificando seu título canônico e caminho de origem. Preserve ordem, seções, condições, restrições, exemplos e critérios de saída. Não substitua o conteúdo por resumo ou por uma descrição do que o instrumento faria.

**Separação entre instrumentos e resultado:** apresente os textos integrais sem confundi-los com a análise ou com o resultado da tarefa. Depois deles, execute a demanda conforme os instrumentos e informe o estado real da operação.

**Sem omissões silenciosas:** se o texto for muito extenso para uma única resposta, divida a entrega em partes identificadas e continue até cobrir integralmente todos os instrumentos acionados, dentro dos limites reais da interface. Se algum arquivo estiver inacessível, incompleto ou exceder um limite técnico incontornável, declare exatamente qual instrumento não pôde ser reproduzido e por quê; não afirme entrega integral nem preencha lacunas por inferência.

**Escopo pertinente:** não é necessário reproduzir indiscriminadamente todo o acervo da Promptária. Reproduza integralmente todos os instrumentos acionados para a demanda, inclusive os fixos e os especializados pertinentes; não omita nenhum desses instrumentos por ele não ter sido explicitamente citado pelo usuário.

**Preservação da fonte:** retornar o texto integral não autoriza alterar o instrumento original. Alterações na Promptária são uma operação separada, sujeita à autorização e às regras de integridade do repositório.

**Verificação de completude:** antes de concluir, confira que cada instrumento acionado tem título, fonte canônica, texto integral retornado e estado de aplicação registrado. A lista de instrumentos retornados deve corresponder à lista de instrumentos efetivamente acionados.

**Invariante de saída:** identificar todos os instrumentos pertinentes → recuperar cada fonte integral → retornar cada texto integral → aplicar os instrumentos → verificar e relatar o resultado. O texto de Nocturna, isoladamente, nunca satisfaz a obrigação de retorno quando outros instrumentos também foram acionados.

**Limite de automação:** esta regra é persistente para agentes e integrações que carreguem AGENTS.md ou este protocolo. O repositório não consegue, por si só, obrigar uma conversa ou ferramenta externa que não carregue essas instruções; nesses ambientes, é necessário conectar explicitamente o arquivo às instruções persistentes da integração.

## Roteamento obrigatório por título da Promptária (regra transversal)

Sempre que uma demanda contiver @GitHub, citar um título/alias de instrumento Promptária ou pedir operação que dependa de instrumento armazenado, o agente deve resolver o destino documental antes de interpretar ou executar a tarefa. Esta regra vale para todos os instrumentos presentes e futuros, não apenas Nocturna.

1. Consulte primeiro Promptária/manifest.json na branch vigente do repositório outocarlos003-lang/Prompt-ria; trate-o como catálogo canônico de IDs, títulos, aliases e caminhos. Não dependa de GitHub Code Search como único mecanismo: se o índice de código estiver indisponível ou não indexado, use a árvore/Contents API e o manifesto.
2. Compare o título completo e os aliases após normalização sem acentos, caixa e pontuação. Prefira correspondência exata de título/alias; só use correspondência parcial se resultar em um único candidato. Se houver múltiplos candidatos, não escolha arbitrariamente.
3. Confirme o registro do instrumento no manifesto e recupere o arquivo canônico integral no caminho declarado (incluindo Index.html quando esse for o caminho). Leia o conteúdo operacional, não apenas o título, o cartão, o excerto da pesquisa ou os metadados. Confirme a fonte e, quando disponível, a integridade/commit.
4. Resolva todos os títulos/aliases explícitos da demanda cumulativamente. O instrumento coordenador e o instrumento operacional fixos são recuperados quando definidos no contexto/protocolo aplicável; instrumentos especializados adicionais são recuperados individualmente. Não confunda instrumentos relacionados com aliases nem funda identidades distintas.
5. Só depois de recuperar os instrumentos, aplique-os à demanda concreta. Preserve o escopo e a autorização do usuário; @GitHub por si só não autoriza escrita. Quando a solicitação pedir atualização do repositório, altere apenas os arquivos necessários, preserve o conteúdo existente e valide por leitura posterior.
6. Se o título não estiver no manifesto, procure a árvore completa e referências cruzadas antes de concluir que está ausente. Se continuar não resolvido, informe os candidatos/caminhos e a limitação; não substitua o instrumento por uma inferência do título.
7. Registre no resultado, proporcionalmente à tarefa: título acionador, ID, caminho canônico, commit/fonte consultada, estado de recuperação integral e operação/verificação efetivamente concluída. Nunca afirme que o instrumento foi recuperado ou aplicado sem evidência.

**Fluxo invariável:** demanda → inventário de títulos → manifesto/árvore → resolução determinística de ID e caminho → recuperação integral → aplicação conforme instrumento → validação → relatório rastreável.

**Limite técnico:** esta regra pré-configura agentes e fluxos que carreguem estas instruções. Não instala, por si só, um gatilho universal em conversas do ChatGPT que não carreguem este arquivo ou não tenham uma integração que consulte a Promptária.
