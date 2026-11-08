# Checklist de reconstrução segura dos workflows

**Estado:** auditoria documental; nenhum workflow foi criado ou executado nesta etapa.

## Arquivos referenciados pelos testes

- `.github/workflows/promptaria-integracao-pr.yml`
- `.github/workflows/promptaria-auto-merge.yml`
- `.github/workflows/promptaria-tests.yml`
- `.github/workflows/promptaria-correfencia.yml`

O diretório `.github/workflows/` está ausente na branch auditada. O teste `tests/test_promptaria_workflow_integrity.py` lê pelo menos os dois primeiros caminhos diretamente, portanto a ausência é uma falha estrutural provável antes mesmo de validar o conteúdo.

## Requisitos para integração via comentário

- Aceitar somente comentário exato `/promptaria merge`.
- Validar associação do autor como `OWNER`.
- Confirmar que o PR está aberto, tem base `main` e vem do mesmo repositório.
- Marcar o PR como pronto quando aplicável.
- Não executar `gh pr merge` nesse workflow.
- Permissões mínimas explícitas; não expor tokens em logs.

## Requisitos para auto-merge

- Aguardar o workflow de verificações denominado `Promptária PR Checks`.
- Consultar todas as verificações do SHA exato testado.
- Prosseguir somente quando todas estiverem concluídas com sucesso.
- Confirmar base `main`, origem no mesmo repositório, PR não rascunho e HEAD atual igual ao SHA testado.
- Fixar a operação ao SHA validado usando `--match-head-commit "$TESTED_SHA"` e estratégia `--squash`.
- Declarar apenas as permissões estritamente necessárias.

## Sequência de validação recomendada

1. Restaurar primeiro o workflow de testes sem privilégios de escrita.
2. Recriar os workflows de integração e auto-merge separadamente, seguindo cada requisito acima.
3. Executar `python -m pytest tests/test_promptaria_workflow_integrity.py -q`.
4. Revisar permissões, filtros de evento, confiança em contribuições externas e correspondência do SHA antes de habilitar auto-merge.
5. Não abrir PR nem afirmar que os workflows estão seguros até haver conteúdo revisado e execução dos testes.

## Limite da evidência

Os requisitos acima foram transcritos da leitura estática dos testes e da auditoria da branch. Não são prova de que workflows estejam instalados, executáveis ou aprovados.
