# Registro de lacunas operacionais do Promptária

## Escopo e estatuto das evidências

Este documento registra uma leitura estática dos pontos de entrada e contratos versionados em `main`. Não representa execução local dos testes, execução de workflows, inspeção de segredos do repositório, nem prova de efeitos em serviços externos. Atualize o registro após executar as verificações indicadas.

## Capacidades identificadas no código/documentação

| Área | Componentes identificados | Estado que a evidência permite afirmar | Verificação necessária |
|---|---|---|---|
| Roteamento contextual | `scripts/promptaria_route_request.py`, `scripts/promptaria_context_router.py` | Implementação versionada para classificar demandas e acumular evidências contextuais | Executar testes de roteamento e casos adversariais de ambiguidade |
| Identidade e correferência | `config/instrument-registry.json`, resolvedor e aliases registrados | Contrato de identidade canônica; somente instrumentos habilitados são acionáveis por título | Validar colisões, aliases, acentos, pontuação, IDs explícitos e instrumentos inativos |
| Execução especializada | `scripts/promptaria_specialized_executor.py`, `scripts/promptaria_contextual_executor.py`, `config/instrument-execution-map.json` | Handlers locais mapeados; o mapa distingue planejamento de execução funcional verificada | Conferir cada handler contra os testes e a integração de workflow atuais |
| Escrita controlada | `scripts/promptaria_executor.py`, `config/promptaria_permissions.json` | Operação genérica `write_text` com simulação padrão, destino restrito e confirmação explícita documentadas | Executar testes de segurança de caminhos, auditoria, interrupção e escrita autorizada em ambiente isolado |
| Auditoria e integridade | `scripts/promptaria_operational_audit.py`, `scripts/promptaria_audit_anchor.py` | Ferramentas versionadas para inventário estático e âncora externa de auditoria | Gerar relatório novo; verificar âncora armazenada fora do domínio de permissões do executor |
| Validação e CI | `.github/workflows/promptaria-tests.yml` e outros workflows listados no inventário do README | Workflows de validação estão versionados e descritos | Examinar execuções recentes, resultados por job, permissões efetivas e proteções de branch |
| Inventário documental | `docs/matriz-instrumento-executor.md`, `docs/auditoria-operacional-reproduzivel.md` | Existem contratos documentais que explicitam lacunas e limites | Regenerar inventário e confirmar que os dados correspondem ao HEAD atual |

## Lacunas prioritárias para verificação

1. **Prova dinâmica atual:** executar `python -m unittest discover -s tests -v` e `node --test tests/*.test.mjs` em ambiente compatível; registrar código de saída, versão do runtime e resumo dos resultados. A existência dos testes não prova que passaram.
2. **Estado de CI:** consultar execuções recentes de todos os workflows relevantes e separar sucesso, falha, cancelamento, ignorado e ausência de execução. Arquivos YAML presentes não demonstram que o workflow está habilitado ou operacional.
3. **Inventário reproduzível:** executar `python scripts/promptaria_operational_audit.py --output artifacts/promptaria-operational-audit.json`, validar o JSON gerado e publicar o relatório como artefato, sem confundir auditoria estática com teste funcional.
4. **Correspondência semântica:** preservar o comportamento conservador de títulos e aliases completos. Se for introduzido ranking aproximado, exigir limiares configuráveis, evidência explicável, testes de colisão e abstenção quando a confiança for insuficiente. Similaridade lexical, isoladamente, não comprova equivalência funcional.
5. **Execução externa:** cada integração externa deve ter um adaptador explícito, permissões mínimas, parâmetros validados, timeout/tratamento de falhas e testes que distingam mock de chamada real. Nenhum handler deve alegar execução externa sem evidência do serviço.
6. **Merge e publicação:** confirmar checks obrigatórios, revisão e regras de proteção antes do merge. A automação de merge existente deve continuar condicionada ao commit efetivamente testado e às políticas do repositório.
7. **Evidência auditável:** registrar versão/commit, comando ou workflow, estado final, artefatos e limitações. Manter a âncora da cadeia fora do alcance de escrita da identidade que gera os registros.

## Critérios para fechar uma lacuna

Uma lacuna só deve ser marcada como resolvida quando houver: (a) mudança implementada e versionada; (b) teste pertinente executado com resultado registrado; (c) integração demonstrada no fluxo aplicável; e (d) limitações residuais explicitadas. Documentação, presença de arquivo, mock, plano gerado ou correspondência de título, isoladamente, não satisfazem esses critérios.

## Próxima sequência operacional

1. Gerar o relatório de auditoria a partir do commit alvo.
2. Executar as suítes Python e JavaScript.
3. Examinar os resultados recentes de GitHub Actions e corrigir falhas reais antes de acrescentar novos pipelines.
4. Priorizar discrepâncias entre registro, catálogo, manifesto, mapa de execução e handlers.
5. Só então implementar adaptadores específicos para lacunas confirmadas, com testes positivos e negativos.
