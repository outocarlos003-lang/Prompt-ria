import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import {
  buildReferenceIndex,
  resolveReference,
  resolveMentions,
  validateReferenceIndex,
  MATCH_TYPES,
  FUNCTION_STATUS,
  ARCHITECTURE_POLICY
} from "./resolver-correferencia.mjs";

const root = process.cwd();
const manifest = JSON.parse(fs.readFileSync(path.join(root, "Promptária", "manifest.json"), "utf8"));
const instruments = manifest.instruments;
const index = buildReferenceIndex(instruments);

assert.deepEqual(validateReferenceIndex(instruments), [], "manifesto possui referências ambíguas/duplicadas");

const exact = resolveReference("ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS: ACIONAMENTO COORDENADO DE INSTRUMENTOS PROMPTUAIS E ARQUITETURA DE ACIONAMENTO, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS, COM CORREFERÊNCIA FUNCIONAL AUTOMÁTICA POR TÍTULOS DOS INSTRUMENTOS PROMPTUAIS, NA QUAL A MENÇÃO GENÉRICA IDENTIFICA O INSTRUMENTO, PRESERVA SUA FUNÇÃO PRÓPRIA E ACIONA SUA EXECUÇÃO, SALVO ATRIBUIÇÃO ESPECÍFICA E INEQUÍVOCA DE FUNÇÃO DIVERSA, COM RECONHECIMENTO MÚTUO, CUMULATIVO, COORDENADO E SIMULTÂNEO DE MÚLTIPLOS TÍTULOS", index);
assert.equal(exact.activation, true);
assert.equal(exact.correferencia, true);
assert.equal(exact.match_type, MATCH_TYPES.EXACT_TITLE);

const normalized = resolveReference("  arquitetura unificada de acionamento, correferência, recuperação e aplicação de instrumentos promptuais: acionamento coordenado de instrumentos promptuais e arquitetura de acionamento, recuperação e aplicação de instrumentos promptuais, com correferência funcional automática por títulos dos instrumentos promptuais, na qual a menção genérica identifica o instrumento, preserva sua função própria e aciona sua execução, salvo atribuição específica e inequívoca de função diversa, com reconhecimento mútuo, cumulativo, coordenado e simultâneo de múltiplos títulos  ", index);
assert.equal(normalized.activation, true);
assert.equal(normalized.match_type, MATCH_TYPES.NORMALIZED_TITLE);

const aliasHint = resolveReference("coordenação", index);
assert.equal(aliasHint.activation, false, "alias não deve acionar instrumento sozinho");
assert.equal(aliasHint.match_type, MATCH_TYPES.ALIAS_HINT);

const unknown = resolveReference("não existe na Promptária", index);
assert.equal(unknown.match_type, MATCH_TYPES.NONE);
assert.equal(unknown.activation, false);

const multi = resolveMentions(
  "ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS: ACIONAMENTO COORDENADO DE INSTRUMENTOS PROMPTUAIS E ARQUITETURA DE ACIONAMENTO, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS, COM CORREFERÊNCIA FUNCIONAL AUTOMÁTICA POR TÍTULOS DOS INSTRUMENTOS PROMPTUAIS, NA QUAL A MENÇÃO GENÉRICA IDENTIFICA O INSTRUMENTO, PRESERVA SUA FUNÇÃO PRÓPRIA E ACIONA SUA EXECUÇÃO, SALVO ATRIBUIÇÃO ESPECÍFICA E INEQUÍVOCA DE FUNÇÃO DIVERSA, COM RECONHECIMENTO MÚTUO, CUMULATIVO, COORDENADO E SIMULTÂNEO DE MÚLTIPLOS TÍTULOS e PROMPT-MATRIZ — ADAPTAÇÃO EXTENSIVA MULTIDIRETÓRIO.",
  instruments,
  index
);
assert.deepEqual(
  [...new Set(multi.map(x => x.instrument_id))].sort(),
  ["instrumento-01", "instrumento-09"]
);
assert.equal(multi.every(x => x.correferencia), true);
assert.equal(multi.every(x => x.function_status === FUNCTION_STATUS.OWN), true);

assert.equal(ARCHITECTURE_POLICY.sections.length, 19);
assert.equal(ARCHITECTURE_POLICY.titleActivates, true);
assert.equal(ARCHITECTURE_POLICY.genericMentionPreservesOwnFunction, true);
assert.equal(ARCHITECTURE_POLICY.diverseFunctionIsException, true);
assert.equal(ARCHITECTURE_POLICY.multipleTitlesAreCumulative, true);
assert.equal(ARCHITECTURE_POLICY.multipleTitlesAreNonExclusive, true);
assert.equal(ARCHITECTURE_POLICY.destinationNocturnaIsNotDefault, true);

console.log("PROMPTÁRIA — CORREFERÊNCIA NODE: TESTES OK");
console.log("Título determinístico: OK");
console.log("Alias não acionante: OK");
console.log("Múltiplos títulos cumulativos: OK");
console.log("Política arquitetural: 19 seções");
