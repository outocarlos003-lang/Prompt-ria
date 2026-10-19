# Fluxo enxuto de contribuição

Objetivo: reduzir etapas repetitivas e tempo de integração sem apagar dados, remover rastreabilidade ou contornar proteções essenciais.

## Caminho padrão
1. Faça mudanças pequenas e focadas em uma branch.
2. Abra um PR com resumo curto, risco e validação executada.
3. Use o rótulo `fast-track` em PRs simples, de baixo risco e originados neste repositório.
4. O workflow `Fast-track integration` encaminha o fluxo; a autoridade central só mescla após conferir os checks da revisão exata.
5. Se os checks estiverem pendentes ou falharem, nenhuma mesclagem automática será feita.

## Como as automações se relacionam
Há workflows de validação e encaminhamento, mas uma única autoridade executa a mesclagem:
- `Auto-integrate PRs into main`: workflow de encaminhamento, sem permissão para mesclar.
- `Fast-track integration`: encaminha PRs internos com o rótulo `fast-track`; não ignora verificações.
- `Promptária Auto-merge`: reage à conclusão dos workflows relevantes, verifica todos os check-runs do SHA testado, bloqueia se houver verificações pendentes ou malsucedidas e só então confere novamente o HEAD antes do squash merge.

A automação exige PR aberta, destino `main`, origem no próprio repositório, ausência de rascunho e correspondência exata entre o SHA testado e o HEAD atual. O sucesso de um workflow isolado não basta. Ao investigar uma integração, confira o nome, o evento e o resultado da execução em Actions. Não remova ou desative workflows até confirmar que suas responsabilidades estão cobertas por outro fluxo.

## Proporcionalidade
- Mudanças de documentação, texto, prompts e correções pequenas devem usar validações rápidas e relevantes.
- Alterações em autenticação, autorização, segredos, dados, dependências críticas, migrações ou infraestrutura exigem revisão e testes proporcionais ao risco.
- Não desative proteção de branch, revisão obrigatória, verificações de segurança relevantes, trilhas de auditoria ou retenção de dados como atalho.
- Prefira checks rápidos, paralelos e incrementais; remova apenas verificações comprovadamente redundantes ou sem valor, após validar com os responsáveis.
- Não apague histórico, artefatos ou metadados associados para acelerar o processo.

## Documentação exigida pelas verificações
O workflow `Promptária - manter README atualizado` aceita `README.md`, `CONTRIBUTING.md` ou arquivos Markdown em `docs/` como documentação editorial para mudanças funcionais. Isso evita exigir uma alteração artificial no README quando a explicação do fluxo pertence ao guia de contribuição.

## Verificação operacional
- Abra um PR pequeno e seguro originado neste repositório.
- Confirme na aba Actions que os checks relevantes terminaram e que nenhum check da revisão está pendente ou falhou.
- Verifique que a integração ocorreu somente depois da validação e do atendimento às regras de proteção.
- Se o workflow falhar, registre a execução e corrija a causa; não contorne as regras de branch para forçar a mesclagem.

## Critério de conclusão
A automação não ignora checks, aprovações, conflitos ou regras do GitHub. Se o repositório não tiver checks obrigatórios, configure apenas os necessários ao projeto em vez de adicionar gates genéricos.

## Manutenção do workflow de sincronização do README

O arquivo `.github/workflows/promptaria-readme-sync.yml` separa duas responsabilidades:
- Em pull requests, validar rastreabilidade dos instrumentos, sintaxe do gerador, documentação das mudanças funcionais e geração determinística do README.
- Em push para `main`, execução agendada ou acionamento manual, atualizar o inventário do README de forma aditiva e criar commit apenas quando houver diferenças.

Ao alterar esse workflow, preserve ambos os jobs, mantenha permissões mínimas e valide o YAML e os checks da pull request antes da integração. Mudanças em `scripts/`, `instruments/`, `config/` ou `.github/workflows/` devem incluir atualização editorial no README, neste guia ou em `docs/*.md`.

## Autoridade única de mesclagem automática

Os workflows `.github/workflows/auto-integrate-main.yml` e `.github/workflows/fast-track-integration.yml` não devem habilitar nem executar mesclagens. A única autoridade de mesclagem é `.github/workflows/promptaria-auto-merge.yml`. Ela examina os check-runs associados ao SHA testado, aceita apenas conclusões `success`, `skipped` ou `neutral`, bloqueia quando há checks pendentes ou malsucedidos e confere novamente o SHA antes de integrar. Mantenha as regras de proteção de branch alinhadas com os checks relevantes; não dependa apenas de um comando `--auto` para impor validações.
