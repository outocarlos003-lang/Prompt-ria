# Evidência de executor para ativação funcional

O comando `scripts/activate_instrument.py --id ID` é uma barreira explícita de ativação, não uma prova automática de que um instrumento é seguro para toda operação.

Antes de habilitar a entrada no registro, o ativador exige uma entrada única para o mesmo ID em `config/instrument-execution-map.json`, com título e caminho idênticos ao registro. O mapa deve apontar para um arquivo de executor existente e para uma função handler declarada nesse arquivo. O status deve ser `specialized_execution_status: implemented`, e o mapa precisa declarar `side_effects_authorized_by_title: false`.

Se o mapa estiver ausente, inválido, incompleto ou divergente, a ativação é recusada. O teste `tests/test_activation_executor_evidence.py` cobre os casos de entrada ausente, divergência de identidade, handler não implementado ou inexistente e autorização de efeitos externos baseada apenas no título.

## Integridade entre artefatos canônicos

O workflow `.github/workflows/test-canonical-artifact-integrity.yml` verifica, em pull requests e em pushes relevantes para `main`, se registro, catálogo, manifesto e mapa de execução mantêm o mesmo conjunto de IDs e a mesma identidade por título e caminho. Também verifica a correspondência entre ativação e visibilidade, impede que instrumentos inativos apareçam como visíveis e exige evidência de handler implementado para instrumentos ativos.

O contrato automatizado está em `tests/test_canonical_artifact_integrity.py`. Para executá-lo localmente:

```bash
python -m unittest discover -s tests -p 'test_canonical_artifact_integrity.py' -v
```

O teste não substitui revisão de permissões nem autoriza efeitos externos. Ele transforma as invariantes estruturais entre os quatro artefatos em condições verificáveis, em vez de depender de inspeção manual.

## Roteamento contextual e evidência de bloqueio

As regras contextuais podem reconhecer uma tarefa que, em princípio, se relaciona com um instrumento ainda inativo. Essa correspondência não autoriza sua seleção: o roteador mantém o ID em `blocked_inactive_instrument_ids`, enquanto `selected_instrument_ids` contém apenas instrumentos habilitados no registro canônico. O executor contextual propaga os bloqueios para a evidência final, sem tratar ausência de seleção como se fosse ativação.

Os testes `tests/test_context_router_activation_gate.py`, `tests/test_promptaria_contextual_executor.py` e `tests/teste-registro-instrumentos.py` cobrem essa separação entre candidato contextual, seleção funcional e bloqueio por ativação.

## Barreira de ativação para IDs explícitos

A passagem de `instrument_ids` ao executor contextual não concede ativação. Cada ID explícito deve existir no registro canônico; IDs desconhecidos encerram a execução com erro. IDs conhecidos, mas desativados, são excluídos da seleção e listados em `routing_evidence.blocked_inactive_instrument_ids`. A seleção explícita continua disponível para instrumentos habilitados, sem permitir que a entrada manual contorne o estado de ativação.

A regressão é coberta por testes em `tests/test_promptaria_contextual_executor.py` para ID inativo explícito e ID desconhecido.

## Verificação

Execute:

```bash
python -m unittest discover -s tests -p 'test_activation_executor_evidence.py' -v
python -m unittest discover -s tests -v
```

Essas verificações avaliam o contrato local de ativação. A existência de um handler não concede permissões externas, não autoriza efeitos colaterais e não substitui revisão das operações e de suas pré-condições.


## Precedência de títulos e aliases no roteador

O roteador e o executor especializado registram os intervalos exatos das correspondências normalizadas. Um título curto ou alias só é suprimido quando cada ocorrência encontrada está inteiramente contida numa correspondência mais longa de outro instrumento; se a referência curta também aparecer separadamente, ambos podem ser selecionados. Limites de palavra são aplicados para rejeitar títulos e aliases colados a caracteres alfanuméricos, como em `xexecução segurax` e `xNocturnaY`; o mesmo vale para IDs e caminhos explícitos, de modo que `github-operationalx` não seja aceito como o ID `github-operational`. Os testes de regressão em `tests/test_promptaria_contextual_executor.py` e `tests/test_promptaria_specialized_executor.py` cobrem correspondências incorporadas, colisões de alias e precedência de título longo.
