# Interconexão funcional entre segmentos

A interconexão compara os metadados canônicos de `continuous_automation` e `recoverable_on_demand`. Uma relação é criada quando existe ao menos uma função ou operação compartilhada após normalização, ou duas palavras-chave coincidentes. Similaridade não redefine identidade.

## Invariantes

- IDs, títulos, caminhos, nós canônicos, quantidade e funções próprias permanecem independentes.
- Cada par recebe ID relacional e nó de coordenação próprios, sem substituir os nós de origem.
- Fase 1: pré-configuração contínua. Fase 2: recuperação sob demanda, somente quando selecionada.
- Correspondência não ativa instrumentos nem autoriza efeitos externos.
- Todas as correspondências qualificadas são preservadas com evidências, caminhos, request_id e relações.

Política: `config/cross-segment-interconnection.json`. Implementação: `scripts/promptaria_cross_segment.py`. Testes: `python -m unittest tests.test_promptaria_cross_segment -v`.
