# Checklist de integridade dos workflows versionados

**Estado:** inventário reconciliado com a árvore atual de main. Este documento descreve os workflows existentes; não presume a existência de automações antigas que não estão versionadas.

## Workflows presentes

1. .github/workflows/promptaria-tests.yml
   - Dispara em pull requests para main.
   - Executa sintaxe e testes do resolvedor JavaScript, testes das salvaguardas de workflows privilegiados e a suíte Python.
   - Permissões de conteúdo somente para leitura.

2. .github/workflows/auto-enable-new-promptual-instruments.yml
   - Dispara em pull requests próprias criadas pelo proprietário.
   - Compara a branch do PR ao SHA-base e classifica somente instrumentos novos.
   - O padrão é recoverable_on_demand; a categoria continuous_automation exige declaração expressa no Markdown e permanece desabilitada.

3. .github/workflows/promptaria-integracao-pr.yml
   - Responde a comentários em pull requests, não a comentários em issues.
   - Exige comentário OWNER exatamente igual a /promptaria merge <HEAD-SHA-atual>.
   - Não executa o merge; valida e prepara/reexecuta os checks para o SHA exato.

4. .github/workflows/promptaria-auto-merge.yml
   - Reage somente à conclusão bem-sucedida de Promptária PR Checks em evento pull_request.
   - Confere completude e sucesso de todos os check-runs, estado/origem/base da PR, HEAD exato e aprovação OWNER.
   - Usa squash merge fixado ao SHA testado.

## Referências que não devem ser tratadas como workflows ativos

Não existem na árvore atual, entre outros, promptaria-correfencia.yml, promptaria-protocolo-mestre.yml, promptaria-pr-checks.yml, promptaria-readme-sync.yml ou promptaria-specialized-execution.yml. O README não deve atribuir a esses caminhos eventos, comandos ou permissões.

## Validação

- Conferir que cada caminho citado no README existe em .github/workflows/.
- Executar python -m unittest tests/test_promptaria_workflow_integrity.py.
- Executar a suíte completa por python -m unittest discover -s tests -p 'test_*.py'.
- Não declarar um workflow operacional apenas porque seu arquivo existe; exigir uma execução real com conclusão observável.
