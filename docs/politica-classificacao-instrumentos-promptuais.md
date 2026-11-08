# Política de classificação de novos instrumentos promptuais

A classificação é determinada no momento da pré-configuração de um arquivo novo em `instruments/*.md`.

## Regra padrão

Quando o título canônico (primeiro cabeçalho H1) contiver a expressão **“Instrumento promptual”**, após normalização de maiúsculas, acentos e pontuação, o registro e o manifesto receberão:

- `category: recoverable_on_demand`
- `classification_basis: default_title_rule`
- `activation.mode: on_demand_title`
- `activation.enabled: true`, `activation.status: active`, `activation.mode: on_demand_title` e `ui.visible: true`

Assim, o instrumento fica efetivamente recuperável por título explícito e visível no catálogo correspondente. Isso habilita somente a recuperação sob demanda: não instala executor, não o inclui na automação contínua e não autoriza efeitos colaterais.

## Exceção expressa

Somente quando houver manifestação expressa em sentido contrário, o arquivo-fonte poderá conter exatamente esta declaração:

`<!-- promptaria: continuous_automation: explicit -->`

Nesse caso, o registro recebe `category: continuous_automation` e `classification_basis: explicit_source_declaration`; permanece desativado até que a arquitetura de automação e suas permissões próprias o habilitem. A declaração é evidência da exceção de classificação, não uma autorização de execução.

## Escopo e preservação

A regra é prospectiva: aplica-se a instrumentos novos descobertos pela rotina de pré-configuração. Não recategoriza retroativamente instrumentos já registrados, não altera suas funções próprias e não converte a mera presença no catálogo em acionamento. O registro canônico, o manifesto de testes e o catálogo gerado devem conservar a categoria e a proveniência da classificação.

Os testes de regressão cobrem o padrão, a exceção expressa, a idempotência e a preservação dos controles de não ativação.
