# Atualização complementar do sistema: correferência automática por título

## Escopo de preservação
Esta atualização é exclusivamente sistêmica. Não edita, renomeia, substitui, funde ou reescreve instrumentos promptuais existentes. Os arquivos de instrumentos continuam sendo a fonte de verdade para título, conteúdo, finalidade e lógica operacional.

## Regras operacionais
- Processar todos os títulos fornecidos, sem parar após a primeira correspondência.
- Preferir correspondência exata após normalização conservadora de maiúsculas/minúsculas, acentos e pontuação.
- Não tratar semelhança temática como identidade.
- Sem correspondência: \`not_found\`; múltiplos arquivos candidatos: \`ambiguous\`, sem escolha arbitrária.
- Distinguir identificação, recuperação, acionamento, tentativa, execução confirmada e resultado validado.
- Manter cada instrumento em arquivo próprio e preservar identidade e proveniência.
- Não impor limite numérico artificial. Limitações materiais devem ser informadas.
- Menção genérica preserva a função própria; função diversa exige indicação expressa ou contexto inequívoco.
- GitHub Actions só processa títulos transmitidos pelo evento ou integração autorizada. Não acessa automaticamente conversas do ChatGPT.
- Escrita em destinos exige destino definido, permissões e validação. Nocturna não é destino padrão.

## Fluxo
\`títulos → detecção individual → correferência → identificação → recuperação → verificação de unicidade → saída rastreável\`

## Componentes adicionados
- \`scripts/promptaria_coreference.py\`: índice de títulos Markdown e resolução de um ou vários títulos.
- \`.github/workflows/promptaria-coreference.yml\`: execução manual e validação em pull requests.

Este documento descreve a camada sistêmica; não substitui o instrumento integral fornecido pelo usuário. Nenhum instrumento promptual existente é alterado.
