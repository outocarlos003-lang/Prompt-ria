# Análise contextual e execução orientada por evidências na Promptária

## Contrato aditivo

Esta camada complementa — não substitui, resume nem reescreve — os contratos existentes do resolvedor, do protocolo-mestre, da pré-configuração de demandas futuras, da correferência funcional, do mapa canônico e dos executores especializados.

Os elementos-base do protocolo-mestre fornecem o quadro comum de interpretação. As personalizações presentes em cada demanda — incluindo texto, títulos, identificadores, campos estruturados, origem, transformação, destinos, validação, cadeia de produção, invariantes e restrições — são preservadas como evidências circunstanciais concatenadas. A análise considera essas evidências em conjunto para determinar quais tarefas são pertinentes naquela ocasião e selecionar os handlers especializados correspondentes. Nenhuma regra encerra a análise na primeira correspondência: as tarefas sustentadas pelo contexto são cumulativas.

## Fluxo funcional

1. Preservar o pedido original e os campos estruturados, inclusive campos futuros desconhecidos.
2. Registrar a proveniência dos valores contextuais por caminho de campo.
3. Incluir os três componentes-base já definidos pelo repositório: coordinator, master-activation e github-operational.
4. Correlacionar evidências de ação, finalidade, objeto, títulos, origem/destino, validação e restrições; selecionar todos os candidatos de tarefa com evidência suficiente.
5. Acrescentar os instrumentos especializados selecionados à lista de títulos resolvidos, mantendo os conflitos de identidade de título explicitamente bloqueados.
6. Executar os handlers locais dedicados e registrar fontes, hashes, resultado, cadeia de evidências e limitações.
7. Validar o resultado. Identificação contextual e execução local do handler são estados distintos de escrita em repositório, publicação ou efeitos externos.

## Regras de integridade

- Título canônico, ID e caminho continuam sendo identidades distintas; colisões não são resolvidas por escolha arbitrária.
- A personalização contextual seleciona tarefas, mas não reescreve a função própria do instrumento nem seu conteúdo-fonte.
- Campos históricos ou declarativos não são aceitos como prova do estado atual sem verificação.
- Uma regra contextual só se ativa com evidência observável; quando não há evidência suficiente, o relatório explicita que apenas os handlers-base foram selecionados.
- A ordem de saída é determinística e deduplicada; todas as categorias correspondentes permanecem registradas.
- A camada não executa código arbitrário extraído dos Markdown e não concede autorização para escrita, exclusão, publicação, deploy ou serviços externos.
- As salvaguardas existentes permanecem vigentes: simulação por padrão, permissões mínimas, validação de destino, executor genérico separado, auditoria e confirmação explícita para escritas reais.

## Uso local

    python scripts/promptaria_preflight.py --request request.json --output artifacts/preflight.json
    python scripts/promptaria_context_router.py --request request.json --output artifacts/contextual-analysis.json
    python scripts/promptaria_contextual_executor.py --request request.json --preflight artifacts/preflight.json --output artifacts/contextual-execution.json
    python -m unittest discover -s tests -v

A análise contextual é evidência auditável da decisão de roteamento, não prova de que uma operação externa foi realizada. O workflow de execução especializada publica o relatório de roteamento junto ao resultado dos handlers.
