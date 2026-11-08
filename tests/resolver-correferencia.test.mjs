import test from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import {
  buildReferenceIndex, resolveMentions, resolveReference, resolveRequest,
  FIXED_OPERATIONAL_INSTRUMENT, FIXED_COORDINATOR_TITLE, FUNCTION_STATUS
} from "../.github/scripts/resolver-correferencia.mjs";

const instruments = [
  { id: "a", title: "INSTRUMENTO ALFA", path: "a/Index.html", aliases: ["alfa"] },
  { id: "b", title: "INSTRUMENTO BETA", path: "b/Index.html", aliases: ["beta"] },
  { id: "c", title: "INSTRUMENTO GAMA", path: "c/Index.html", aliases: ["gama"] }
];
const index = buildReferenceIndex(instruments);

test("título canônico em menção genérica ativa a função própria", () => {
  const result = resolveMentions("Aplique o INSTRUMENTO ALFA à demanda.", instruments, index);
  assert.equal(result.length, 1);
  assert.equal(result[0].instrument_id, "a");
  assert.equal(result[0].activation, true);
  assert.equal(result[0].function_status, FUNCTION_STATUS.OWN);
});

test("atribuição diversa é local e não bloqueia outro instrumento", () => {
  const request = "INSTRUMENTO ALFA deve atuar como uma função diferente. INSTRUMENTO BETA é necessário para a demanda.";
  const result = resolveMentions(request, instruments, index);
  assert.equal(result.length, 2);
  assert.equal(result.find(x => x.instrument_id === "a").activation, false);
  assert.equal(result.find(x => x.instrument_id === "a").function_status, FUNCTION_STATUS.DIVERSE);
  assert.equal(result.find(x => x.instrument_id === "b").activation, true);
});

test("exceção atribuída a um título não bloqueia outro na mesma frase", () => {
  const request = "INSTRUMENTO ALFA deve atuar como uma função diferente, enquanto INSTRUMENTO BETA deve preservar sua função.";
  const result = resolveMentions(request, instruments, index);
  assert.equal(result.find(x => x.instrument_id === "a").activation, false);
  assert.equal(result.find(x => x.instrument_id === "b").activation, true);
});

test("a exceção só afeta o título que a precede, não títulos anteriores", () => {
  const request = "INSTRUMENTO ALFA, INSTRUMENTO BETA deve atuar como uma função diferente.";
  const result = resolveMentions(request, instruments, index);
  assert.equal(result.find(x => x.instrument_id === "a").activation, true);
  assert.equal(result.find(x => x.instrument_id === "b").activation, false);
});

test("coordenador fixo é ativado com demanda transmitida sem alterar o catálogo", () => {
  const withCoordinator = [...instruments, { id: "coord", title: FIXED_COORDINATOR_TITLE, path: "coord/Index.html", aliases: [] }];
  const result = resolveRequest("Aplique o INSTRUMENTO ALFA.", withCoordinator);
  assert.equal(result.coordinator.activation, true);
  assert.equal(result.coordinator.instrument_id, "coord");
  assert.equal(result.operational_fixed.activation, true);
});

test("múltiplos títulos são reconhecidos cumulativamente", () => {
  const result = resolveRequest("INSTRUMENTO ALFA e INSTRUMENTO BETA devem ser aplicados.", instruments);
  assert.equal(result.activated.length, 2);
  assert.equal(result.multiple_titles, true);
  assert.equal(result.traceability.length, 2);
  assert.match(result.traceability[0].relação_com_demais, /cumulativa/);
});

test("acentos e pontuação preservam os offsets do texto original", () => {
  const request = "Solicitação: ação útil. INSTRUMENTO ALFA, por favor.";
  const result = resolveMentions(request, instruments, index);
  assert.equal(result.length, 1);
  assert.equal(request.slice(result[0].start, result[0].end), "INSTRUMENTO ALFA");
});

test("alias normalizado único resolve o instrumento", () => {
  const result = resolveReference("alfa", index);
  assert.equal(result.activation, true);
  assert.equal(result.match_type, "canonical_alias");
  assert.equal(result.instrument_id, "a");
});

test("colisão entre título e alias de instrumentos distintos é ambígua", () => {
  const catalog = [
    { id: "canonical", title: "Alfa", path: "canonical.md", aliases: [] },
    { id: "other", title: "Instrumento Beta", path: "beta.md", aliases: ["Alfa"] }
  ];
  const result = resolveReference("Alfa", buildReferenceIndex(catalog));
  assert.equal(result.activation, false);
  assert.equal(result.match_type, "ambiguous_title_alias");
  assert.deepEqual(new Set(result.candidates), new Set(["canonical", "other"]));
});


test("a ausência de requisição não inventa demanda nem aciona o instrumento fixo", () => {
  const result = resolveRequest("   ", instruments);
  assert.equal(result.transmitted, false);
  assert.equal(result.matches.length, 0);
  assert.equal(result.operational_fixed.activation, false);
  assert.deepEqual(result.operational_fixed.operations, ["inserir", "recuperar", "aplicar"]);
  assert.equal(FIXED_OPERATIONAL_INSTRUMENT.title, result.operational_fixed.title);
});

test("acentos, hífens e menções repetidas seguem a normalização canônica", () => {
  const catalog = [{ id: "accent", title: "Ação-Útil", path: "accent.md" }];
  const result = resolveMentions("Aplicar acao util e AÇÃO-ÚTIL.", catalog);
  assert.equal(result.length, 2);
  assert.ok(result.every(item => item.activation === true));
  assert.deepEqual(result.map(item => item.function_status), ["own", "own"]);
});

test("menções repetidas recebem decisões de exceção independentes", () => {
  const request = "INSTRUMENTO ALFA deve atuar como uma função diferente. Depois, INSTRUMENTO ALFA deve preservar sua função própria.";
  const result = resolveMentions(request, instruments, index).filter(item => item.instrument_id === "a");
  assert.equal(result.length, 2);
  assert.equal(result[0].activation, false);
  assert.equal(result[0].function_status, "diverse");
  assert.equal(result[1].activation, true);
  assert.equal(result[1].function_status, "own");
});

test("contrato compartilhado de paridade Python/JavaScript", () => {
  const fixture = JSON.parse(readFileSync(new URL("./fixtures/correference-parity.json", import.meta.url), "utf8"));
  const catalog = fixture.instruments.map(item => ({
    id: item.id, title: item.title, path: item.path, aliases: []
  }));
  for (const scenario of fixture.cases) {
    const scenarioCatalog = (scenario.instruments ?? fixture.instruments).map(item => ({
      id: item.id, title: item.title, path: item.path, aliases: []
    }));
    const actual = resolveMentions(scenario.request, scenarioCatalog).map(item => ({
      title: item.title,
      activation: item.activation,
      function_status: item.function_status
    }));
    assert.deepEqual(actual, scenario.expected, `caso de paridade: ${scenario.id}`);
  }
});

test("referência explícita por ID e caminho é validada no catálogo", () => {
  const pathCatalog = instruments.map(item => ({ ...item, path: `instruments/${item.id}.md` }));
  const pathIndex = buildReferenceIndex(pathCatalog);
  const byId = resolveReference("instrument_id:a", pathIndex);
  assert.equal(byId.activation, true);
  assert.equal(byId.match_type, "explicit_id");
  assert.equal(byId.instrument_id, "a");
  const byPath = resolveReference("instrument_path:instruments/b.md", pathIndex);
  assert.equal(byPath.activation, true);
  assert.equal(byPath.match_type, "explicit_path");
  assert.equal(byPath.instrument_id, "b");
  const missing = resolveReference("instrument_id:missing", pathIndex);
  assert.equal(missing.activation, false);
  assert.equal(missing.match_type, "unresolved_explicit_id");
});

test("menções explícitas por ID/caminho são resolvidas no texto", () => {
  const pathCatalog = instruments.map(item => ({ ...item, path: `instruments/${item.id}.md` }));
  const pathIndex = buildReferenceIndex(pathCatalog);
  const byId = resolveMentions("instrument_id:a", pathCatalog, pathIndex);
  assert.equal(byId.length, 1);
  assert.equal(byId[0].match_type, "explicit_id");
  assert.equal(byId[0].instrument_id, "a");
  const byPath = resolveMentions("instrument_path:instruments/b.md", pathCatalog, pathIndex);
  assert.equal(byPath.length, 1);
  assert.equal(byPath[0].match_type, "explicit_path");
  assert.equal(byPath[0].instrument_id, "b");
});

test("instrumento desabilitado não resolve por título nem alias", () => {
  const catalog = [
    { id: "enabled", title: "Ativo", path: "active.md", aliases: ["nome compartilhado"], enabled: true },
    { id: "disabled", title: "Desativado", path: "disabled.md", aliases: ["desativado alias"], enabled: false }
  ];
  const disabledIndex = buildReferenceIndex(catalog);
  assert.equal(resolveReference("Desativado", disabledIndex).activation, false);
  assert.equal(resolveReference("desativado alias", disabledIndex).activation, false);
  const explicit = resolveMentions("instrument_id:disabled", catalog, disabledIndex);
  assert.equal(explicit[0].activation, false);
  assert.equal(explicit[0].match_type, "disabled_reference");
});

test("alias duplicado em instrumentos habilitados não ativa nenhum candidato", () => {
  const catalog = [
    { id: "first", title: "Primeiro", path: "first.md", aliases: ["compartilhado"] },
    { id: "second", title: "Segundo", path: "second.md", aliases: ["compartilhado"] }
  ];
  const result = resolveMentions("compartilhado", catalog);
  assert.equal(result.length, 2);
  assert.ok(result.every(item => !item.activation && item.function_status === "ambiguous"));
});

test("menção genérica e silêncio preservam a função própria", () => {
  const result = resolveMentions("INSTRUMENTO GAMA.", instruments, index);
  assert.equal(result[0].activation, true);
  assert.equal(result[0].exception_scope, null);
});

test("títulos do manifesto resolvem somente quando a identidade é única", () => {
  const manifest = JSON.parse(readFileSync(new URL("./manifest.json", import.meta.url), "utf8"));
  assert.ok(Array.isArray(manifest.instruments), "manifesto deve expor instruments");
  assert.ok(manifest.instruments.length > 0, "catálogo não pode estar vazio");
  const catalog = manifest.instruments;
  const catalogIndex = buildReferenceIndex(catalog);
  const normalize = value => String(value ?? "")
    .normalize("NFKD").replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("pt-BR").replace(/[\u200b-\u200f\ufeff]/g, "")
    .replace(/[^\p{L}\p{N}_\s-]/gu, " ").replace(/[\s-]+/g, " ").trim();
  const titleCounts = new Map();
  for (const instrument of catalog) {
    const key = normalize(instrument.title);
    titleCounts.set(key, (titleCounts.get(key) ?? 0) + 1);
  }
  const ids = new Set();
  const paths = new Set();
  for (const instrument of catalog) {
    assert.ok(instrument.id, "cada instrumento precisa de id");
    assert.ok(instrument.title, `instrumento ${instrument.id} precisa de título canônico`);
    assert.ok(instrument.path, `instrumento ${instrument.id} precisa de caminho`);
    assert.ok(!ids.has(instrument.id), `id duplicado: ${instrument.id}`);
    ids.add(instrument.id);
    assert.ok(!paths.has(instrument.path), `caminho duplicado no catálogo: ${instrument.path}`);
    paths.add(instrument.path);
    const fileUrl = instrument.path.startsWith("Promptária/")
      ? new URL(`./${instrument.path.slice("Promptária/".length)}`, import.meta.url)
      : new URL(`../${instrument.path}`, import.meta.url);
    assert.ok(existsSync(fileUrl), `arquivo de destino ausente para "${instrument.title}": ${instrument.path}`);

    const ambiguous = titleCounts.get(normalize(instrument.title)) > 1;
    const exact = resolveReference(instrument.title, catalogIndex);
    assert.equal(exact.activation, !ambiguous, `decisão canônica incorreta: ${instrument.title}`);
    if (ambiguous) {
      assert.equal(exact.match_type, "ambiguous_title");
      assert.ok(exact.candidates.includes(instrument.id), "todos os candidatos ambíguos devem ser rastreáveis");
    } else {
      assert.equal(exact.instrument_id, instrument.id, `título encaminhado ao id incorreto: ${instrument.title}`);
      assert.equal(exact.path, instrument.path, `título encaminhado ao caminho incorreto: ${instrument.title}`);
    }

    const normalized = resolveReference(instrument.title.toLocaleLowerCase(), catalogIndex);
    assert.equal(normalized.activation, !ambiguous, `decisão de título normalizado incorreta: ${instrument.title}`);
    if (ambiguous) {
      assert.equal(normalized.match_type, "ambiguous_title");
    } else {
      assert.equal(normalized.instrument_id, instrument.id, `variação normalizada encaminhada ao id incorreto: ${instrument.title}`);
      assert.equal(normalized.path, instrument.path, `variação normalizada encaminhada ao caminho incorreto: ${instrument.title}`);
    }
  }
});
