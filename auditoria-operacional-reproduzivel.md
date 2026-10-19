# Auditoria operacional reproduzível

A auditoria estática agora pode ser regenerada a partir dos instrumentos, do registro canônico, do manifesto, do mapa de execução, dos handlers, dos testes e dos workflows versionados.

```bash
python scripts/promptaria_operational_audit.py --output artifacts/promptaria-operational-audit.json
python -m unittest tests.test_promptaria_operational_audit -v
```

O relatório atribui exatamente uma categoria por instrumento:

- `already_automated`: somente quando o mapa declara explicitamente `functional_execution_verified: true` e a identidade, o handler, os testes e a integração ao workflow também estão presentes.
- `partially_automated`: existe handler especializado mapeado, mas a execução funcional integral não está comprovada.
- `no_executor`: não há handler especializado comprovado ou há lacuna de identidade/fonte.

A ferramenta não executa os textos dos instrumentos, não modifica o registro canônico e não concede permissões. Ela é uma auditoria estática conservadora; resultados de execução real, permissões externas, segredos, proteções de branch e serviços devem ser verificados separadamente. A categoria `already_automated` depende de uma declaração explícita no contrato do executor, para impedir que código ou testes isolados sejam tratados como prova suficiente.
