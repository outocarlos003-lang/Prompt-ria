# Matriz instrumento → executor → permissões → evidências

## Estado e interpretação

Esta matriz distingue quatro coisas que não devem ser confundidas:

1. **Resolução:** identificar o instrumento canônico e recuperar sua fonte.
2. **Handler especializado implementado:** executar uma transformação local, determinística e específica do ID, com evidência de integridade.
3. **Execução integral do prompt:** seguir toda a semântica operacional de um instrumento em uma demanda real; a presença de um handler, por si só, não comprova que todas as instruções do documento foram executadas.
4. **Efeito externo:** gravar conteúdo, alterar configurações, publicar, abrir/mesclar PRs ou operar serviços. Nenhum título concede essa autorização.

O mapa de máquina é `config/instrument-execution-map.json`. A implementação está em `scripts/promptaria_specialized_executor.py`; a cobertura positiva/negativa está em `tests/test_promptaria_specialized_executor.py` e a integridade de evidência de ativação em `tests/test_activation_executor_evidence.py`.

## Capacidades compartilhadas

- **Resolver e preflight:** `scripts/promptaria_resolver.py` e `scripts/promptaria_preflight.py` identificam referências e validam correspondências.
- **Executor especializado local:** `scripts/promptaria_specialized_executor.py` despacha por ID canônico para um handler registrado, valida a identidade entre manifesto, mapa e registry, recupera a fonte e emite SHA-256 e resultado estruturado.
- **Evidência:** cada resultado especializado registra o ID/caminho da fonte, o hash, o estado da execução e a lista de efeitos colaterais; os testes confirmam a cobertura de todos os IDs do manifesto e a ausência de efeitos externos nesses handlers.
- **Executor genérico de escrita:** `scripts/promptaria_executor.py` implementa apenas `write_text`, sujeito a `config/promptaria_permissions.json`, destinos sob `artifacts/`, autorização explícita, `dry_run=false`, confirmação exata do `operation_id` e trilha de auditoria.
- **Workflow manual:** `.github/workflows/promptaria-specialized-execution.yml` executa preflight/análise/handlers e publica JSON como artefato. A permissão de conteúdo é somente leitura; o workflow não autoriza escrita externa.

## Matriz por instrumento

| ID canônico | Handler | Capacidade local implementada | Limite importante |
|---|---|---|---|
| `github-operational` | `handler_github_operational` | Recupera e verifica a fonte, constrói envelope de demanda e registra relações de identidade | Não executa operações externas do GitHub |
| `coordinator` | `handler_coordinator` | Coordena IDs selecionados, ordem de execução, fontes/hash e gates de validação | Não substitui a execução dos handlers selecionados |
| `master-activation` | `handler_master_activation` | Constrói plano de ativação com gates explícitos | Não ativa permissões nem efeitos externos |
| `master-execution` | `handler_master_execution` | Executa checklist local de primeira passagem e associa hashes | Checklist não prova, sozinho, execução integral do prompt |
| `functional-correference-architecture` | `handler_functional_correference` | Emite relatório de correspondências e bloqueia identidades ambíguas | Não escolhe arbitrariamente entre títulos colidentes |
| `future-demand-preconfiguration` | `handler_future_preconfiguration` | Preserva o objeto estruturado, gera ID determinístico quando ausente e mantém os campos originais | Não dispara a operação descrita no objeto |
| `catalog-sitemap-preconfiguration` | `handler_catalog_sitemap` | Audita instrumentos Markdown e presença de artefatos legados | Não cria catálogo/sitemap nem publica conteúdo |
| `promptaria-instrument-template` | `handler_promptaria_instrument_template` | Inspeciona a fonte do modelo e registra sua integridade | A presença do modelo não o ativa |
| `protocol-update-integrity` | `handler_protocol_update_integrity` | Produz plano local de integridade e rastreabilidade | Não modifica os instrumentos originais |
| `nocturna-arquitetura-necessidade-identidade-sistemica` | `handler_nocturna_architecture` | Recupera a fonte local e registra a proveniência disponível | Não comprova acesso ou atualização de serviços externos da Nocturna |

O estado `specialized_execution_status=implemented` significa que o handler local correspondente existe e passa pela validação de cobertura/identidade. **Não** significa que o instrumento tenha permissão para escrever, que o prompt inteiro tenha sido executado em todos os contextos ou que algum serviço externo tenha sido alterado.

## Resolução de identidade e colisões

1. A identidade canônica é o ID do manifesto com caminho e título conferidos no mapa e no registry.
2. Títulos/aliases normalizados que apontem para mais de um instrumento devem falhar fechados. Use ID ou caminho explícito para desambiguar; nunca escolha pelo primeiro resultado.
3. A existência de handlers para dois instrumentos não elimina a ambiguidade de uma menção textual.
4. O antigo segmento fixo “parte 2” foi consolidado na identidade canônica `github-operational`; não deve ser reintroduzido como ID/caminho concorrente sem decisão explícita e atualização sincronizada dos catálogos.

## Permissões e limites de segurança

- Resolver, recuperar, planejar e emitir evidências são operações locais sem efeitos externos.
- `side_effects_authorized_by_title` deve permanecer `false` para todos os instrumentos.
- O executor genérico não é um executor universal: escrita controlada só pode ocorrer em `artifacts/`, com autorização por operação e confirmação exata.
- Alterações de arquivos-fonte, configuração, permissões, workflows, serviços externos, criação/merge de PRs e publicação exigem uma operação específica, autorização aplicável, validação de pré-condições e evidência verificável do resultado.
- O workflow especializado é manual e read-only; o artefato JSON comprova o resultado daquele run, não um deploy ou efeito externo.

## Critérios de verificação

- O mapa, o manifesto e o registry cobrem exatamente os mesmos IDs e mantêm título/caminho idênticos.
- Cada ID tem um handler existente e testes positivos/negativos.
- A execução de teste cobre todos os handlers e valida o SHA-256 da fonte recuperada.
- Correspondências ambíguas permanecem bloqueadas até desambiguação explícita.
- Nenhuma menção de título concede permissão para efeitos colaterais.
- Relatórios de execução distinguem resultado local, autorização de escrita e efeitos externos efetivamente observados.
