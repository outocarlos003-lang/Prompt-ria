# Interconexão funcional entre segmentos

A interconexão relaciona os instrumentos habilitados de `continuous_automation` e `recoverable_on_demand` sem fundi-los. A correspondência é calculada sobre funções, operações, palavras-chave e conceitos semânticos normalizados. Todas as relações qualificadas são preservadas e ordenadas por evidência.

## Fases independentes e procedimento compartilhado

1. **Pré-configuração contínua:** prepara contexto, critérios, dependências e referências; não executa por si só a função de um instrumento recuperável.
2. **Recuperação sob demanda:** recupera e aplica somente o instrumento selecionado, preservando sua função e contrato próprios.
3. **Reconciliação rastreável:** correlaciona evidências e resultados sem misturar autoria, estado ou identidade dos instrumentos.

## Invariantes

- Quantidade, IDs canônicos, títulos, caminhos e nós originais permanecem inalterados.
- Cada par recebe um `pair_id`, um `correlation_id` e um nó de coordenação compartilhado. Esses identificadores relacionam os instrumentos; não substituem seus IDs.
- O `request_id` é propagado do envelope de pré-configuração às relações e ao resultado.
- A similaridade produz uma relação procedimental, nunca uma fusão, clonagem ou alteração de localização.
- A correspondência não ativa instrumentos, não executa operações e não autoriza efeitos externos.
- Correspondências ambíguas continuam bloqueadas pela resolução canônica.

Política: `config/cross-segment-interconnection.json`.
Implementação: `scripts/promptaria_interconnection.py`.
Integração no pré-processamento: `scripts/promptaria_preflight.py`.
Validação: `python -m unittest tests.test_promptaria_interconnection -v`.
