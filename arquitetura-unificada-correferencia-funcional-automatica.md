# ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS: ACIONAMENTO COORDENADO DE INSTRUMENTOS PROMPTUAIS E ARQUITETURA DE ACIONAMENTO, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS, COM CORREFERÊNCIA FUNCIONAL AUTOMÁTICA POR TÍTULOS DOS INSTRUMENTOS PROMPTUAIS, NA QUAL A MENÇÃO GENÉRICA IDENTIFICA O INSTRUMENTO, PRESERVA SUA FUNÇÃO PRÓPRIA E ACIONA SUA EXECUÇÃO, SALVO ATRIBUIÇÃO ESPECÍFICA E INEQUÍVOCA DE FUNÇÃO DIVERSA, COM RECONHECIMENTO MÚTUO, CUMULATIVO, COORDENADO E SIMULTÂNEO DE MÚLTIPLOS TÍTULOS

## 1. Finalidade e escopo
Estabelecer uma pré-configuração reutilizável para identificar, recuperar, correlacionar e planejar a aplicação de instrumentos promptuais em demandas futuras, preservando a arquitetura vigente da Promptária.

## 2. Fonte canônica
A coleção versionada em `instruments/*.md` e seus primeiros cabeçalhos Markdown são a fonte canônica vigente. Não presumir que exista `Promptária/manifest.json`, sitemap ou outra fonte paralela sem confirmar sua presença e seu contrato.

## 3. Identidade por título
O título canônico completo identifica um instrumento. A comparação pode normalizar Unicode, caixa, espaços e pontuação, mas deve conservar o título original e o caminho de origem para rastreabilidade.

## 4. Correspondência exata e normalizada
Uma correspondência exata ou normalizada do título pode identificar o instrumento. Não usar correspondência parcial arbitrária que confunda títulos diferentes.

## 5. Aliases e pistas
Aliases, palavras-chave e menções genéricas podem servir como pistas de recuperação, mas não devem, isoladamente, acionar um instrumento como se fossem seu título canônico.

## 6. Recuperação integral
Recuperar o conteúdo integral do instrumento encontrado. Não resumir, substituir, reescrever nem omitir instruções próprias quando a operação solicitada exigir preservação integral.

## 7. Correferência funcional
Quando um título identificar um instrumento, manter sua identidade e função próprias na demanda correlacionada. Não converter a simples identificação em alegação de execução já concluída.

## 8. Exceção por função diversa
Só uma atribuição específica e inequívoca de função diversa pode afastar a função própria. Se a atribuição for ambígua ou depender de semântica contextual, registrar a exceção como pendente de revisão, em vez de decidir por heurística lexical.

## 9. Múltiplos títulos cumulativos
Reconhecer todos os títulos mencionados na mesma demanda. As correspondências são cumulativas, coordenadas e simultâneas, não exclusivas; não parar na primeira correspondência nem impor limite arbitrário de cardinalidade.

## 10. Componentes-base vigentes
Preservar os três componentes-base definidos pelo resolvedor existente: arquitetura coordenadora, protocolo-mestre e instrumento operacional GitHub. Não alterar suas identidades nem seu contrato de resultado.

## 11. Pré-configuração futura
Incluir esta arquitetura de correferência no plano de cada demanda futura quando o arquivo estiver presente, sem duplicar caminhos já selecionados. A inclusão automática significa disponibilidade no plano, não execução automática de instruções especializadas.

## 12. Destino e segurança
Validar destinos como caminhos relativos POSIX e preservar as proteções existentes contra caminhos absolutos, traversal, segmentos ambíguos, `.git`, separadores Windows e caracteres de controle.

## 13. Autorização explícita
Manter a simulação como padrão. Qualquer escrita real exige mecanismo executor separado, destino permitido e autorização explícita; o reconhecimento de título nunca constitui autorização de escrita.

## 14. Estados de execução
Distinguir identificação, recuperação, inclusão no plano, revisão, tentativa, execução confirmada e resultado validado. Só declarar um estado quando houver evidência técnica correspondente.

## 15. Auditoria e rastreabilidade
Preservar os identificadores de instrumento, caminhos, estados, resultados e mecanismos de auditoria já existentes. Não remover nem enfraquecer controles de integridade ou reconciliação.

## 16. Compatibilidade arquitetural
A implementação deve estender a arquitetura Python, o executor separado, os workflows e os contratos de resultado existentes. Não introduzir uma implementação paralela baseada em Node.js, manifesto ou diretórios presumidos sem migração explícita e testes compatíveis.

## 17. Falhas fechadas
Se um componente obrigatório estiver ausente, um título for ambíguo, a recuperação falhar ou uma validação não passar, registrar a falha claramente e não inventar conteúdo ou declarar sucesso.

## 18. Verificação e regressão
Testar título canônico, normalização, alias não acionante, título desconhecido, múltiplas correspondências, preservação da função própria, ausência de duplicação, componentes obrigatórios e o contrato que impede alegações falsas de execução. Executar a suíte existente antes de declarar a atualização validada.

## 19. Limites e conclusão verificável
O workflow só processa demandas entregues por eventos GitHub autorizados. Não lê conversas arbitrárias do ChatGPT nem concede permissões externas. Considerar uma demanda concluída apenas quando os critérios solicitados e suas evidências forem verificados; caso contrário, informar precisamente o que ficou pendente.


## 20. Interconexão canônica com o instrumento operacional fixo

A automação de correspondência por título mantém sua própria identidade documental, mas referencia o instrumento operacional fixo pela identidade canônica do registro, sem criar um segundo instrumento nem confundir os papéis.

- Instrumento operacional referido: `github-operational`.
- Nó canônico: `instrument:github-operational`.
- Registro autoritativo: `config/instrument-registry.json`.
- Fonte integral: `instruments/acione-a-promptaria-pelo-github.md`.
- Vínculo com esta automação: `functional-correference-architecture->github-operational` e `github-operational->functional-correference-architecture`.
- A correspondência por título identifica e encaminha; o instrumento canônico recupera a fonte, preserva metadados, estrutura o envelope da demanda e fornece evidências de rastreabilidade. A menção não concede autorização de escrita nem prova execução externa.
- O protocolo-mestre e a pré-configuração padrão apontam para o mesmo ID e nó. Os títulos, caminhos e funções próprios dos segmentos permanecem preservados.

## 21. Contrato intersegmentos do nó operacional canônico

Esta automação conserva sua identidade própria (`functional-correference-architecture`) e conecta-se bidirecionalmente ao instrumento operacional único, sem absorver nem substituir suas funções.

- **Registro de identidade:** `config/instrument-registry.json`.
- **ID operacional referenciado:** `github-operational`.
- **Nó interconectado:** `instrument:github-operational`.
- **Fonte operacional integral:** `instruments/acione-a-promptaria-pelo-github.md`.
- **Segmento de protocolo-mestre:** `instruments/protocolo-mestre-acionamento-automatico.md`.
- **Pré-configuração documental:** `docs/preconfiguracao-protocolo-mestre-e-correferencia.md`.
- **Arestas obrigatórias:** `functional-correference-architecture->github-operational`, `github-operational->functional-correference-architecture`, `title-correspondence-automation->instrument:github-operational` e `instrument:github-operational->title-correspondence-automation`.

### Divisão de responsabilidades sem perda de função

1. Esta automação identifica títulos canônicos, normaliza somente para comparação, preserva proveniência, resolve correspondências cumulativas e encaminha cada identidade encontrada.
2. O instrumento `github-operational` executa o papel operacional compartilhado: inspecionar/localizar recursos, recuperar a fonte integral, preservar e normalizar o envelope da demanda, correlacionar aliases e IDs, encaminhar a operação autorizada e manter evidências de rastreabilidade.
3. O protocolo-mestre continua coordenando a demanda, incluindo os componentes-base, as instruções especializadas e a verificação de satisfação; a pré-configuração conserva o contexto estruturado e os estados da operação.
4. Os três papéis são complementares e cumulativos. Nenhum título, alias, palavra-chave ou aresta autoriza fundir identidades, apagar funções próprias, presumir execução ou conceder permissão de escrita.
5. O registro é a autoridade para ID, caminho, nó e ativação. Catálogo e manifesto devem refletir o mesmo ID e caminho; mudanças na identidade canônica exigem atualização coordenada e validação dos três artefatos.

A cadeia de rastreio exigida é: demanda/origem → título ou pista de recuperação → ID canônico → nó `instrument:github-operational` → fonte integral → função pertinente → operação autorizada → evidência → validação. Registrar separadamente identificação, recuperação, planejamento, tentativa, execução confirmada e resultado validado.
## 22. Identidade canônica e interconexão do instrumento coordenador unificado

Este instrumento conserva a identidade documental `functional-correference-architecture` e o caminho `instruments/arquitetura-unificada-correferencia-funcional-automatica.md`. Sua identidade não é substituída pela do instrumento operacional fixo. A integração no catálogo usa o título integral como identificador canônico e mantém a correferência explícita com os dois segmentos relacionados.

- **ID canônico deste instrumento coordenador:** `functional-correference-architecture`.
- **Nó deste instrumento:** `instrument:functional-correference-architecture`.
- **Registro autoritativo:** `config/instrument-registry.json`.
- **Catálogo derivado:** `config/instrument-catalog.json`.
- **Instrumento operacional fixo:** ID `github-operational`, nó `instrument:github-operational`, fonte `instruments/acione-a-promptaria-pelo-github.md`.
- **Segmento de protocolo-mestre:** ID `master-activation`, nó `instrument:master-activation`, fonte `instruments/protocolo-mestre-acionamento-automatico.md`.
- **Pré-configuração documental:** `docs/preconfiguracao-protocolo-mestre-e-correferencia.md`.

### Contrato de correspondência e preservação funcional

1. A arquitetura unificada coordena a correferência, a recuperação, a interpretação conjunta, a contextualização, a parametrização, a adaptação, a execução e a validação dos instrumentos participantes.
2. A automação de correspondência por título preserva sua função de identificar títulos, resolver correspondências cumulativas, registrar proveniência e encaminhar cada identidade encontrada; não seleciona apenas a primeira correspondência.
3. O protocolo-mestre preserva sua função de coordenar a demanda, as dependências, os componentes-base e os critérios de satisfação verificável.
4. O instrumento fixo `github-operational` preserva a função operacional de localizar e recuperar conteúdo efetivo, normalizar e preservar o envelope da demanda, manter metadados e aliases e fornecer evidências de rastreabilidade.
5. A pré-configuração padrão preserva contexto, parâmetros, origem, destino, autorização, dependências e estados operacionais. Plano, acionamento, tentativa, execução confirmada e resultado validado permanecem estados distintos.
6. As funções são cumulativas e complementares. Nenhum segmento absorve, substitui ou reduz os demais; o uso compartilhado de relações não cria IDs ou arquivos-fonte paralelos.
7. A identidade do instrumento coordenador e a identidade do instrumento fixo são distintas. As relações entre eles são explícitas e bidirecionais quando indicado no registro.

### Relações canônicas

- `functional-correference-architecture->github-operational`
- `github-operational->functional-correference-architecture`
- `functional-correference-architecture->master-activation`
- `master-activation->functional-correference-architecture`
- `title-correspondence-automation->functional-correference-architecture`
- `functional-correference-architecture->title-correspondence-automation`
- `functional-correference-architecture->standard-preconfiguration`
- `standard-preconfiguration->functional-correference-architecture`
- `instrument:functional-correference-architecture->instrument-registry`
- `instrument-registry->instrument:functional-correference-architecture`

A cadeia de rastreabilidade deve permitir percorrer título integral → ID canônico → nó → arquivo-fonte → função → operação → evidência → validação, bem como recuperar a partir do arquivo-fonte os segmentos relacionados. Uma relação registrada não comprova, por si só, execução externa nem autoriza escrita.

## Fonte integral canônica

A versão integral recebida em PDF foi transcrita para [arquitetura-unificada-acionamento-correferencia-recuperacao-aplicacao.md](./arquitetura-unificada-acionamento-correferencia-recuperacao-aplicacao.md). Este arquivo continua preservado como documento de arquitetura e referência funcional; o arquivo vinculado contém o texto integral da versão-fonte. O registro, o catálogo e o manifesto apontam para a fonte integral canônica, mantendo este documento como referência relacionada.
