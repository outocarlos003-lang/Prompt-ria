# Integridade de identidade no executor especializado

Antes de executar handlers, o executor compara o conjunto de IDs e os campos canônicos `title` e `path` entre o manifesto (`tests/manifest.json`), o mapa de execução (`config/instrument-execution-map.json`) e o registro (`config/instrument-registry.json`). Divergências bloqueiam a execução em vez de permitir que fontes conflitantes sejam usadas como se fossem uma identidade única.

Os caminhos de fonte também são resolvidos e precisam permanecer dentro da raiz do repositório. Caminhos absolutos ou que escapem da raiz, inclusive por meio de resolução de diretórios, são rejeitados antes da leitura.

Essas verificações protegem a consistência dos dados locais. Não comprovam que integrações externas funcionam nem autorizam efeitos externos.

Campos de identidade ausentes, vazios ou com tipo diferente de texto também são rejeitados de forma controlada; a validação não deve falhar com exceções de tipo ao inspecionar catálogos malformados.

## Autorização de ativação

A seleção por ID explícito ou por resultado de pré-configuração não substitui a autorização do registro. Antes de ler fontes ou chamar handlers, o executor exige `activation.enabled == true` para cada instrumento selecionado. Um resultado de pré-configuração não pode elevar o estado de um instrumento desativado; o estado canônico do registro é revalidado no executor.

O executor contextual trata o roteador como gerador de candidatos, não como autoridade de ativação. Instrumentos desativados são excluídos da seleção implícita e registrados em `blocked_inactive_instrument_ids`. IDs explicitamente solicitados continuam sujeitos à verificação de ativação do executor especializado e são rejeitados se estiverem desativados.
