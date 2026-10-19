# Integridade do catálogo do executor especializado

O executor especializado carrega três fontes de identidade: o manifesto `tests/manifest.json`, o mapa `config/instrument-execution-map.json` e o registro `config/instrument-registry.json`.

Antes de indexar entradas por ID, `index_catalog_entries` verifica que `instruments` é uma lista, que cada item é um objeto com ID textual não vazio e que nenhum ID se repete na mesma fonte. Uma duplicata é erro bloqueante: não se permite que a última entrada sobrescreva silenciosamente a anterior durante a construção de um dicionário.

O manifesto e o mapa também precisam cobrir exatamente o mesmo conjunto de IDs. A resolução consulta o registro validado antes de considerar instrumentos ativos. Isso detecta duplicatas dentro de cada fonte; não substitui a auditoria cruzada de títulos, caminhos e presença entre fontes.

## Regressões

`tests/test_promptaria_specialized_executor.py` cobre IDs duplicados no manifesto, no mapa de execução e no registro. A suíte de regressão do GitHub Actions executa esses testes com `python -m unittest discover -s tests -v`.

## Limites

A validação de identidade não prova que uma integração externa funciona, nem concede autorização para efeitos colaterais. A execução continua sujeita aos contratos específicos de cada handler e às verificações de autorização aplicáveis.
