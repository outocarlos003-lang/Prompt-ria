# Regra de desambiguação de instrumentos

Esta regra aplica-se à identificação por título, alias e correferência no registro Promptária.

## Precedência de identidade

1. **ID explícito**: quando a solicitação indicar um ID canônico, esse ID identifica o instrumento.
2. **Caminho explícito do repositório**: um caminho canônico como `instruments/arquivo.md` identifica o registro correspondente.
3. **Título canônico normalizado**: usar apenas se houver exatamente um instrumento habilitado correspondente.
4. **Alias normalizado**: usar apenas se houver exatamente um instrumento habilitado correspondente.
5. **Correspondência parcial ou menção genérica**: pode sugerir candidatos, mas não resolve uma colisão por si só.

A normalização ignora diferenças de caixa, acentos, pontuação e variações de espaços/hífens.

## Quando há ambiguidade

- Se dois ou mais instrumentos **habilitados** correspondem ao mesmo título ou alias normalizado, não ativar nenhum por essa menção. Exigir ID explícito ou caminho do repositório.
- Se a colisão envolver apenas um instrumento habilitado e outros desabilitados, a resolução funcional pode selecionar somente o habilitado. Instrumentos desabilitados nunca são promovidos automaticamente.
- Se título e alias apontarem para registros habilitados diferentes, tratar como ambíguo, mesmo que uma das correspondências pareça mais provável.
- Se não houver correspondência única, retornar candidatos e o motivo da ambiguidade; não inventar uma escolha nem afirmar execução.
- Uma atribuição específica de função diferente continua sendo uma exceção local à ocorrência mencionada; não altera a identidade do instrumento nem outras ocorrências da mesma solicitação.

## Exemplo de referência explícita

Use o identificador canônico do registro ou o caminho canônico do arquivo na solicitação, por exemplo:

- `instrument_id:github-operational`
- `instrument_path:instruments/acione-a-promptaria-pelo-github.md`

Os resolvedores Python e JavaScript implementam referências explícitas por ID/caminho e correspondência por alias normalizado. Cada referência é validada contra o catálogo recebido; texto parecido com um ID que não exista no registro não é uma referência válida. Se o catálogo fornecer `activation.enabled` ou `enabled`, entradas desabilitadas ficam fora da resolução funcional.

## Garantias e limites

A auditoria estrutural distingue colisões bloqueantes de colisões que envolvem entradas desabilitadas. Os testes cobrem o resolvedor Python, o resolvedor JavaScript e o contrato entre eles. Uma correspondência válida significa identidade resolvida, não execução: recuperação de conteúdo, seleção do instrumento, autorização e execução continuam sendo estados distintos.
