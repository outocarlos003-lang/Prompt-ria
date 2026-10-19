# Guia de integração para qualquer agente de IA

Este repositório usa instruções e automações independentes de fornecedor. O objetivo é permitir que diferentes agentes de programação — por exemplo, ChatGPT/Codex, GitHub Copilot, Claude, Gemini, Cursor, Windsurf ou agentes próprios — executem o mesmo fluxo quando estiverem conectados ao repositório e tiverem as ferramentas/permissões necessárias.

## Inicialização obrigatória

1. Leia o arquivo raiz `AGENTS.md` integralmente antes de agir. Ele é a fonte operacional comum e define escopo, recuperação de instrumentos, execução, verificação e limites de autorização.
2. Leia `.github/AUTOPILOT.md` para o fluxo de pull requests e os workflows relacionados.
3. Leia `config/preconfiguracao-integridade-sistemica.md`, `config/interface-traceability-current.json` e `config/traceability-graph-current.json` antes de alterar interface, arquitetura, funções, destinos ou relações.
4. Consulte instruções específicas que a plataforma também carregar. Elas complementam as regras comuns; não as substituem nem ampliam a autorização.
5. Confirme que o ambiente tem acesso de leitura/escrita ao repositório e ferramentas para abrir/atualizar PRs e consultar GitHub Actions. Se não tiver, informe exatamente o que falta; não alegue execução.

## Fluxo de trabalho compartilhado

1. Identifique o pedido, o escopo, o destino e um critério observável de conclusão.
2. Inspecione os arquivos e o histórico pertinentes. Procure issues/PRs equivalentes antes de duplicar registros.
3. Resolva os termos, nós, funções, arquivos, destinos e relações afetados usando os manifests de rastreabilidade; registre relações não comprovadas como pendentes, sem inferi-las como fatos.
4. Faça alterações em uma branch de trabalho, preservando arquivos não relacionados.
5. Execute `python -m unittest discover -s tests -v` e as verificações específicas do projeto.
6. Abra ou atualize um PR com resumo, testes e limitações. Não marque a autorização de merge por padrão.
7. Marque `[x] Permito merge automático após validações passarem` somente quando o pedido atual autorizar claramente a conclusão ponta a ponta e o merge daquele PR específico.
8. Aguarde/consulte o workflow `Promptária PR Checks`, o workflow de pré-configuração e o artefato de prévia quando aplicável. O artefato baixável não é um deploy público.
9. O GitHub Actions pode solicitar auto-merge apenas se o PR estiver aberto, o SHA atual for exatamente o SHA validado, os checks passarem e a caixa de autorização estiver marcada. Proteções, revisões e checks obrigatórios do repositório continuam valendo.
10. Após o merge, confirme o estado do PR e o commit de merge. Verifique publicação/deploy separadamente.
11. Informe evidências observadas, o que foi alterado, o que foi verificado e qualquer bloqueio real.

## Contrato de rastreabilidade de interface e produção

Toda mudança que acrescente, remova ou altere um termo visível, placeholder, controle acionável, nó visual, função, arquivo ou destino deve manter correspondência no manifesto de rastreabilidade e no grafo de relações. A validação automática falha quando um texto visível não possui entrada correspondente ou quando uma relação não contém origem, destino, função e evidência.

A seleção de instrumentos para demandas futuras é cumulativa: `scripts/promptaria_context_router.py` conserva todos os candidatos sustentados por evidência contextual e ativa a regra de integridade quando a demanda envolver rastreabilidade, relações, funções, arquivos, origem, destino ou validação. Isso não concede autorização adicional para efeitos externos.

## Compatibilidade e limites

- O workflow de CI e o mecanismo de auto-merge são executados pelo GitHub Actions e não dependem de um modelo específico.
- As instruções são portáveis, mas não são um gatilho mágico: cada agente/ambiente precisa carregar `AGENTS.md` (ou receber seu conteúdo como contexto), possuir conectividade com o GitHub e dispor de credenciais e permissões válidas.
- Quando possível, configure a integração para carregar `AGENTS.md` automaticamente e inclua este guia nas instruções persistentes do agente. Em agentes que não reconheçam esse padrão, copie o caminho e as regras deste guia para a configuração do projeto.
- Não existe configuração dentro do repositório capaz de conceder acesso a contas externas, alterar permissões do agente ou obrigar uma conversa externa a executar ações.
- Nunca contorne CI, branch protection ou revisões obrigatórias. A autorização de merge é específica para cada PR e não autoriza operações destrutivas, mudanças de segredos/permissões ou alterações de segurança não solicitadas.
