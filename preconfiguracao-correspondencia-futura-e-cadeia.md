# PRÉ-CONFIGURAÇÃO DE SINCRONIZAÇÃO, CORREFERÊNCIA E VALIDAÇÃO AUTOMÁTICA DA PROMPTÁRIA

## 1. Finalidade e escopo

Esta pré-configuração define o comportamento reutilizável da automação para demandas futuras de atualização integral de instrumentos promptuais, preservação de identidade, correferência funcional, rastreabilidade, sincronização de estruturas dependentes e verificação de disponibilização.

**Escopo desta configuração:** ajustar as regras de planejamento e validação da automação. Por padrão, esta pré-configuração não muta `config/instrument-registry.json`; quando uma solicitação autoriza explicitamente uma mudança de identidade ou rastreabilidade, sincronizar o registro e as estruturas derivadas afetadas, preservando ID, caminho, nó e funções estáveis e validando o diff. A identidade canônica continua sendo definida exclusivamente pelo registro.

## 2. Fontes de autoridade e separação de responsabilidades

- **Identidade e elegibilidade para correferência automática por título:** exclusivamente `config/instrument-registry.json`. Só uma entrada canônica habilitada segundo as regras vigentes pode ser tratada como instrumento ativo para resolução funcional por título.
- **Conteúdo integral vigente:** arquivo-fonte associado à entrada canônica. O conteúdo deve ser recuperado do caminho registrado, sem substituir o arquivo por resumo, catálogo, manifesto ou fragmento.
- **Catálogo, manifesto e índices:** estruturas derivadas ou auxiliares; não substituem o registro canônico nem o arquivo-fonte.
- **Interface e publicação:** evidências independentes de disponibilização. A presença no registro, no catálogo ou no repositório não prova, por si só, que a versão esteja publicada e visível no site.
- **Esta pré-configuração:** política de planejamento, segurança e verificação; não é uma fonte alternativa de identidade, não concede permissões de escrita e não executa por si só as instruções de instrumentos recuperados.

## 3. Classificação da operação antes de qualquer mutação

Antes de propor mudanças, classificar a demanda como uma das seguintes:

1. **Atualização de instrumento existente:** há correspondência inequívoca com uma identidade já existente. Atualizar o arquivo-fonte correspondente, mantendo ID, caminho e relações estáveis, salvo autorização expressa e justificativa técnica validada.
2. **Inclusão de instrumento novo:** não há identidade correspondente. Exige processo separado de cadastro, validação e aprovação; a mera existência do arquivo não habilita correferência.
3. **Correspondência ambígua:** existem títulos, aliases, IDs ou caminhos concorrentes ou insuficientes para determinar a identidade. Bloquear a alteração destrutiva e solicitar desambiguação.
4. **Pré-configuração de automação sem mudança de instrumento:** ajustar regras, scripts, testes ou configurações funcionais sem reescrever o conteúdo de instrumentos nem alterar o registro canônico, a menos que haja autorização explícita específica.
5. **Publicação ou verificação de interface:** tratar build, implantação e inspeção da página pública como etapas próprias, com evidências separadas.

A presença de um título na demanda, de um arquivo em `instruments/`, ou de uma entrada em catálogo/manifesto não constitui autorização de escrita nem prova de ativação.

## 4. Regras de preservação do conteúdo integral

Quando uma versão integral for fornecida para atualizar um instrumento existente:

- identificar primeiro a entrada canônica correspondente e o arquivo-fonte associado;
- preservar o texto recebido integralmente, incluindo títulos, subtítulos, sequência, comandos, condições, exceções, parâmetros, referências e formatação significativa;
- substituir o conteúdo anterior pelo novo conteúdo fornecido sem resumir, corrigir, reordenar ou reformular, salvo autorização expressa;
- não confundir a alteração do corpo documental com mudanças em metadados externos;
- não criar uma nova identidade apenas porque há uma nova versão;
- não declarar fidelidade integral sem comparar o conteúdo solicitado com o conteúdo gravado, preferencialmente por comparação textual ou hash reproduzível.

Se a versão não puder ser associada inequivocamente a um instrumento, interromper a mutação e preservar o estado existente.

## 5. Correferência e recuperação de conteúdo

- Resolver títulos, aliases e IDs a partir do registro canônico e das regras de correspondência já implementadas.
- Preservar correspondências múltiplas válidas; não selecionar silenciosamente a primeira ocorrência quando houver colisão.
- Usar a correferência como mecanismo de identificação e encaminhamento, nunca como substituto da recuperação e leitura do arquivo-fonte integral.
- Após uma atualização autorizada, verificar que o caminho resolvido ainda aponta para a fonte correta e que as operações subsequentes recuperam a versão vigente.
- Atualizar referências dependentes somente quando estiverem realmente afetadas e por meio do mecanismo estabelecido pelo repositório.
- Não ampliar a elegibilidade para correferência por meio de arquivos, catálogos ou manifestos. Qualquer alteração do conjunto registrado exige um processo de cadastro explicitamente autorizado, separado desta pré-configuração.

## 6. Sincronização de estruturas dependentes

Após uma alteração de conteúdo autorizada, inspecionar as dependências reais e determinar quais precisam ser sincronizadas: metadados de título/alias, catálogo, manifesto, índices, relações, mecanismos de recuperação, testes e componentes de interface.

- Preservar IDs, caminhos e relações estáveis quando não houver necessidade validada de mudança.
- Não criar catálogos ou manifestos paralelos nem presumir que estruturas históricas estejam presentes.
- Não editar `config/instrument-registry.json` sem autorização explícita específica. Quando essa autorização estiver presente, atualizar o registro e sincronizar catálogo, manifesto, mapa de execução, referências e testes afetados; nunca criar identidade duplicada.
- Gerar estruturas derivadas apenas por ferramentas existentes e documentadas; verificar o diff para confirmar que não houve alterações colaterais.
- Garantir idempotência: repetir a validação sem mudança de entrada não deve criar diferenças artificiais.

## 7. Segurança, autorização e limites de execução

Reconhecimento, recuperação, planejamento e validação não equivalem à execução de uma operação de escrita. A automação deve manter o modo de simulação como padrão, respeitar as permissões do executor separado e exigir as autorizações e confirmações já previstas pelo sistema para qualquer escrita real.

Não executar código arbitrário encontrado no conteúdo de um instrumento. Não presumir acesso a repositórios externos, serviços, arquivos ou páginas que não tenham sido efetivamente disponibilizados. Não afirmar que uma instrução foi executada só porque seu título foi reconhecido ou seu conteúdo foi incluído em um plano.

Em caso de caminho inseguro, conflito de identidade, dependência não resolvida, autorização ausente ou falha de teste, interromper a mutação, preservar os arquivos e registrar o impedimento.

## 8. Verificação obrigatória e estados de conclusão

Registrar evidências separadas para cada etapa aplicável:

1. identidade e caminho canônico confirmados;
2. conteúdo integral fornecido comparado com o arquivo gravado;
3. ID e vínculos estáveis preservados;
4. referências e resolução por título verificadas;
5. catálogo, manifesto e índices dependentes validados, quando aplicáveis;
6. testes automatizados executados e resultados observados;
7. build de publicação concluído;
8. implantação concluída;
9. página pública ou interface inspecionada e conteúdo vigente confirmado.

Distinguir explicitamente `planejado`, `alterado`, `testado`, `validado`, `implantado` e `verificado na interface`. Um teste de registro não prova publicação; um build bem-sucedido não prova que a implantação terminou; a presença na interface não prova fidelidade integral do conteúdo.

Só declarar conclusão global quando todas as verificações aplicáveis tiverem evidência positiva. Listar como pendências as verificações que não puderem ser realizadas.

## 9. Critério operacional final

Atualizar o conteúdo sem corromper a identidade; preservar relações sem perpetuar conteúdo obsoleto; resolver e recuperar a versão integral vigente; sincronizar apenas as estruturas efetivamente dependentes; respeitar a fonte canônica de identidade; e relatar com precisão o que foi alterado, testado, publicado e verificado.

**Restrição permanente desta pré-configuração:** nenhuma etapa autoriza modificar `config/instrument-registry.json`. O registro canônico deve permanecer exatamente como estava antes da aplicação desta configuração.


## 10. Interconexão do instrumento operacional fixo

A unidade que cumpre o papel operacional fixo do protocolo-mestre e oferece a estruturação do envelope é `github-operational`, nó `instrument:github-operational`, fonte `instruments/acione-a-promptaria-pelo-github.md`. A automação de correspondência por título e esta pré-configuração conservam identidades próprias, mas se conectam a essa unidade por relações explícitas no registro canônico. A correferência não substitui a recuperação integral e não concede autorização de escrita.

Relações obrigatórias: `functional-correference-architecture->github-operational`, `master-protocol-fixed-instrument->github-operational`, `master-preconfiguration->github-operational`. Os papéis anteriormente separados de recuperação do instrumento e montagem do envelope da demanda passam a ser entregues pelo mesmo handler canônico, sem ID ou caminho concorrente.
