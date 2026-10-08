import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { buildReferenceIndex, resolveReference, resolveMentions, validateReferenceIndex, MATCH_TYPES } from "./resolver-correferencia.mjs";

const root = process.cwd();
const manifest = JSON.parse(fs.readFileSync(path.join(root, "Promptária", "manifest.json"), "utf8"));
const instruments = manifest.instruments;
const index = buildReferenceIndex(instruments);

assert.deepEqual(validateReferenceIndex(instruments), [], "manifesto possui referências ambíguas/duplicadas");

const cases = [
  ["instrumento-05", "id", MATCH_TYPES.ID],
  ["Prompt-Matriz", "prompt-matriz", MATCH_TYPES.ALIAS],
  ["Rastreio GitHub", "rastreio GitHub", MATCH_TYPES.ALIAS],
  ["CORREFERÊNCIA FUNCIONAL AUTOMÁTICA", "correferência funcional automática", MATCH_TYPES.ALIAS],
  ["  prompt-matriz  ", "prompt-matriz", MATCH_TYPES.ALIAS]
];

for (const [input] of cases) {
  const resolved = resolveReference(input, index);
  assert.equal(resolved.activation, true, input);
}

assert.equal(resolveReference("acionamento", index).activation, false, "termo genérico não deve ativar instrumento silenciosamente");
assert.equal(resolveReference("não existe na Promptária", index).match_type, MATCH_TYPES.NONE);

const multi = resolveMentions(
  "Use a Prompt-Matriz junto com a correferência funcional automática.",
  instruments,
  index
);
assert.deepEqual(
  [...new Set(multi.map(x => x.instrument_id))].sort(),
  ["instrumento-05", "instrumento-09"]
);

console.log("PROMPTÁRIA — CORREFERÊNCIA: TESTES OK");
console.log("Casos determinísticos: 5");
console.log("Múltiplas menções: OK");
console.log("Ambiguidade/negativo: OK");
