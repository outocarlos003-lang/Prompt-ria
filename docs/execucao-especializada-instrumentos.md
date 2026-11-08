# Execução especializada dos instrumentos Promptária

## Contrato

Cada ID do `tests/manifest.json` tem um handler próprio registrado em `scripts/promptaria_specialized_executor.py` e mapeado em `config/instrument-execution-map.json`. O dispatcher valida o manifesto e o mapa, recupera cada fonte Markdown, confirma que o primeiro heading coincide com o título canônico e calcula SHA-256 antes de executar a função específica.

## Handlers

| ID | Função executada |
| --- | --- |
| `github-operational` | Recupera e verifica a fonte e emite evidência de integridade. |
| `coordinator` | Coordena instrumentos selecionados, ordem e gates de validação. |
| `master-activation` | Constrói plano de ativação com componentes-base e gates explícitos. |
| `master-execution` | Executa checklist estruturado de interpretação, recuperação, planejamento e validação. |
| `functional-correference-architecture` | Emite relatório de correspondências cumulativas e colisões bloqueadas. |
| `fixed-prompt-instrument-part-2` | Constrói envelope que separa demanda, fontes e estado da operação. |
| `future-demand-preconfiguration` | Preserva todos os campos do pedido estruturado e gera/preserva `request_id`. |
| `catalog-sitemap-preconfiguration` | Audita fonte canônica e existência de arquivos legados sem criar uma fonte paralela. |

## Uso local

Prepare um JSON de demanda:

```json
{
  "request": "Validar a cadeia de execução da Promptária",
  "instrument_ids": ["master-execution", "coordinator"]
}
```

Execute:

```sh
python scripts/promptaria_preflight.py --request request.json --output artifacts/preflight.json
python scripts/promptaria_specialized_executor.py --request request.json --preflight artifacts/preflight.json --output artifacts/specialized-execution.json
python -m unittest discover -s tests -v
```

`instrument_ids` é opcional se os títulos forem identificados sem ambiguidade no preflight. Quando dois instrumentos partilham título normalizado, a execução por título é bloqueada até que a solicitação informe um ID explícito. Nenhum handler escolhe arbitrariamente.

## Workflow GitHub Actions

Use Actions → **Promptária — receber e resolver demanda** → Run workflow. Informe `request_json` como objeto JSON com `request` (texto ou objeto estruturado) e, opcionalmente, `instrument_ids` (lista de IDs canônicos). O workflow chama o executor contextual, que carrega o conteúdo integral de todos os instrumentos `continuous_automation` habilitados como contexto inerte, roteia a demanda e executa apenas os handlers especializados dos instrumentos recuperáveis efetivamente selecionados. O resultado JSON é publicado como artefato para inspeção. O workflow tem permissão `contents: read`, não altera o repositório e não executa efeitos externos.

Exemplo de `request_json`:

```json
{
  "request": "Validar a cadeia de correferência por título",
  "request_id": "req-validacao-001"
}
```

O conteúdo contínuo é incluído no campo `continuous_preconfiguration.components`, com `loaded_as_context=true`, `title_resolvable=false` e `execution_performed=false`. A inclusão como contexto não transforma esses instrumentos em handlers nem os promove à recuperação individual por título.

## Sincronização do inventário documental

O script `scripts/sync_readme_inventory.py` reconstrói as seções de inventário do README a partir das árvores reais de instrumentos, scripts, workflows, documentação, testes e configurações. O workflow de classificação de novos instrumentos executa essa sincronização e inclui `README.md` no mesmo commit das atualizações de metadados. Para alterações estruturais feitas por outros fluxos, execute `python scripts/sync_readme_inventory.py`; `--check` detecta divergências sem manter a alteração gerada.

## Limites declarados

O status `completed` significa que o handler especializado selecionado foi executado e produziu o resultado documentado. Não significa que ocorreu uma escrita no repositório, uma publicação, uma chamada a serviço externo ou a execução arbitrária das instruções textuais do Markdown. Os handlers atuais são transformações locais determinísticas e de leitura; `side_effects` permanece vazio. Escritas reais continuam sujeitas ao executor genérico, à allowlist `artifacts/`, à autorização, ao `dry_run=false` e à confirmação exata da operação.
