export const FUNCTION_STATUS = Object.freeze({ OWN: "own", DIVERSE: "diverse", AMBIGUOUS: "ambiguous" });
export const FIXED_COORDINATOR_TITLE = "ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS";
export const FIXED_OPERATIONAL_INSTRUMENT = Object.freeze({
  id: "github-operational",
  title: "Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas",
  path: "instruments/acione-a-promptaria-pelo-github.md",
  operations: ["inserir", "recuperar", "aplicar"]
});
const norm = s => String(s ?? "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
const escapeRegex = s => s.replace(/[.*+?^$\x7b\x7d()|[\]\\]/g, "\\$&");
function normalizeWithOffsets(text) {
  let value = "";
  const starts = [], ends = [];
  let offset = 0;
  for (const character of text) {
    const start = offset;
    offset += character.length;
    const normalized = character.normalize("NFD").replace(/[\\u0300-\\u036f]/g, "").toLowerCase();
    for (const ch of normalized) {
      const out = /[a-z0-9]/.test(ch) ? ch : " ";
      if (out === " " && (!value || value.endsWith(" "))) continue;
      value += out;
      starts.push(start);
      ends.push(offset);
    }
  }
  if (value.endsWith(" ")) { value = value.slice(0, -1); starts.pop(); ends.pop(); }
  return { value, starts, ends };
}
const enabled = x => x && x.enabled !== false;
const aliases = x => Array.isArray(x.aliases) ? x.aliases : [];
const result = (x, extra = {}) => ({ instrument_id: x?.id ?? null, title: x?.title ?? "", path: x?.path ?? null, activation: false, function_status: "own", match_type: "unresolved", start: 0, end: 0, exception_scope: null, ...extra });

export function buildReferenceIndex(instruments = []) {
  const list = Array.isArray(instruments) ? instruments : [];
  const terms = [];
  const byId = new Map();
  const byPath = new Map();
  for (const item of list) {
    if (item.id != null) byId.set(String(item.id), [...(byId.get(String(item.id)) ?? []), item]);
    if (item.path != null) byPath.set(norm(item.path), [...(byPath.get(norm(item.path)) ?? []), item]);
    if (!enabled(item)) continue;
    for (const [value, kind] of [[item.title, "canonical_title"], ...aliases(item).map(a => [a, "canonical_alias"])]) {
      if (norm(value)) terms.push({ item, value: String(value), key: norm(value), kind });
    }
  }
  terms.sort((a, b) => b.value.length - a.value.length);
  return { instruments: list, terms, byId, byPath };
}
const indexOf = x => Array.isArray(x) ? buildReferenceIndex(x) : x?.terms ? x : buildReferenceIndex([]);

export function resolveReference(reference, catalog) {
  const index = indexOf(catalog);
  const raw = String(reference ?? "").trim();
  let list, matchType;
  let m = raw.match(/^instrument_id:(.+)$/i);
  if (m) {
    list = index.byId.get(m[1].trim()) ?? [];
    matchType = "explicit_id";
  } else if ((m = raw.match(/^instrument_path:(.+)$/i))) {
    list = index.byPath.get(norm(m[1].trim())) ?? [];
    matchType = "explicit_path";
  } else {
    const key = norm(raw);
    list = index.terms.filter(t => t.key === key).map(t => t.item);
    const kinds = index.terms.filter(t => t.key === key);
    const hasTitle = kinds.some(t => t.kind === "canonical_title");
    const hasAlias = kinds.some(t => t.kind === "canonical_alias");
    matchType = hasTitle && hasAlias ? "ambiguous_title_alias" : hasTitle ? "canonical_title" : "canonical_alias";
  }
  const active = [...new Map(list.filter(enabled).map(x => [x.id, x])).values()];
  if (active.length === 1) return result(active[0], { activation: true, match_type: matchType });
  if (active.length > 1) return result(active[0], { function_status: "ambiguous", match_type: matchType === "explicit_id" ? "ambiguous_id" : matchType === "explicit_path" ? "ambiguous_path" : matchType === "ambiguous_title_alias" ? "ambiguous_title_alias" : matchType === "canonical_title" ? "ambiguous_title" : "ambiguous_title_alias", candidates: active.map(x => x.id) });
  const disabled = list[0];
  return result(disabled, { match_type: disabled ? "disabled_reference" : matchType === "explicit_id" ? "unresolved_explicit_id" : matchType === "explicit_path" ? "unresolved_explicit_path" : "unresolved", candidates: list.map(x => x.id) });
}

export function resolveMentions(request, instruments = [], suppliedIndex) {
  const text = String(request ?? "");
  if (!text.trim()) return [];
  const index = indexOf(suppliedIndex ?? instruments);
  const out = [];
  const explicit = /instrument_(?:id|path):[^\s,;]+/gi;
  const occupied = [];
  for (const m of text.matchAll(explicit)) {
    const start = m.index ?? 0, end = start + m[0].length;
    const r = resolveReference(m[0], index);
    out.push({ ...r, start, end, function_status: r.activation ? "own" : r.function_status });
    occupied.push([start, end]);
  }

  const candidates = [];
  const normalizedText = normalizeWithOffsets(text);
  for (const term of index.terms) {
    const re = new RegExp("(^| )(" + escapeRegex(term.key) + ")(?=$| )", "g");
    for (const m of normalizedText.value.matchAll(re)) {
      const normalizedStart = (m.index ?? 0) + m[1].length;
      const normalizedEnd = normalizedStart + m[2].length;
      const start = normalizedText.starts[normalizedStart];
      const end = normalizedText.ends[normalizedEnd - 1];
      if (start == null || end == null || occupied.some(([a,b]) => start < b && end > a)) continue;
      if (candidates.some(x => x.start === start && x.end === end && x.term.item.id === term.item.id)) continue;
      candidates.push({start,end,term});
    }
  }
  candidates.sort((a,b) => a.start - b.start || b.end - a.end);
  // Prefer the longest canonical mention when a short alias is contained in its title.
  const filteredCandidates = candidates.filter(candidate => !candidates.some(other =>
    other !== candidate && other.start <= candidate.start && other.end >= candidate.end &&
    (other.start < candidate.start || other.end > candidate.end)
  ));
  candidates.length = 0;
  candidates.push(...filteredCandidates);
  const exceptionPattern = /função diferente|função diversa|papel diferente|papel diverso/gi;
  const exceptionMatches = [...text.matchAll(exceptionPattern)].map(m => ({start:m.index ?? 0,end:(m.index ?? 0)+m[0].length}));
  for (let i = 0; i < candidates.length; i++) {
    const {start,end,term} = candidates[i];
    if (out.some(x => x.start === start && x.end === end && x.instrument_id === term.item.id)) continue;
    const collisions = index.terms.filter(t => t.key === term.key);
    const ids = [...new Set(collisions.map(t => t.item.id))];
    const clauseStart = Math.max(text.lastIndexOf(".",start-1),text.lastIndexOf("!",start-1),text.lastIndexOf("?",start-1),text.lastIndexOf(";",start-1),text.lastIndexOf("\n",start-1))+1;
    const clauseEndCandidates = [text.indexOf(".",end),text.indexOf("!",end),text.indexOf("?",end),text.indexOf(";",end),text.indexOf("\n",end)].filter(n=>n>=0);
    const clauseEnd = clauseEndCandidates.length ? Math.min(...clauseEndCandidates) : text.length;
    const nextMention = candidates.slice(i+1).find(x=>x.start<clauseEnd)?.start ?? clauseEnd;
    const prefix = text.slice(clauseStart,start);
    const suffix = text.slice(end,nextMention);
    const afterMarker = exceptionMatches.some(e=>e.start>=end && e.start<nextMention && e.end<=clauseEnd);
    const beforeMarker = /função diferente|função diversa|papel diferente|papel diverso/i.test(prefix) &&
      !/preservar|manter|própria/i.test(suffix);
    const exception = afterMarker || beforeMarker;
    const ambiguous = ids.length > 1;
    const hasTitle = collisions.some(t=>t.kind==="canonical_title");
    const hasAlias = collisions.some(t=>t.kind==="canonical_alias");
    const ambiguousType = hasTitle && hasAlias ? "ambiguous_title_alias" : hasTitle ? "ambiguous_title" : "ambiguous_alias";
    out.push(result(term.item,{start,end,activation:!ambiguous&&!exception,function_status:ambiguous?"ambiguous":exception?"diverse":"own",match_type:ambiguous?ambiguousType:term.kind,...(ambiguous?{candidates:ids}:{}),exception_scope:exception?{type:"local",start,end}:null}));
  }
  return out.sort((a,b)=>a.start-b.start||a.end-b.end);
}

export function resolveRequest(request, instruments = []) {
  const text = String(request ?? "");
  const transmitted = Boolean(text.trim());
  const index = buildReferenceIndex(instruments);
  const matches = transmitted ? resolveMentions(text, instruments, index) : [];
  const activated = matches.filter(x => x.activation);
  const coord = index.instruments.find(x => x.id === "coord" || norm(x.title) === norm(FIXED_COORDINATOR_TITLE));
  const operational = index.instruments.find(x => x.id === FIXED_OPERATIONAL_INSTRUMENT.id || norm(x.title) === norm(FIXED_OPERATIONAL_INSTRUMENT.title)) ?? FIXED_OPERATIONAL_INSTRUMENT;
  return {
    transmitted, matches, activated,
    multiple_titles: new Set(activated.map(x => x.instrument_id)).size > 1,
    traceability: activated.map(x => ({ instrument_id: x.instrument_id, title: x.title, path: x.path, relação_com_demais: "ativação cumulativa com os demais instrumentos identificados" })),
    coordinator: coord ? result(coord, { activation: transmitted, match_type: "fixed_coordinator" }) : { instrument_id: null, title: FIXED_COORDINATOR_TITLE, path: null, activation: transmitted, match_type: "fixed_coordinator" },
    operational_fixed: { instrument_id: operational.id, title: operational.title, path: operational.path, activation: transmitted, operations: [...FIXED_OPERATIONAL_INSTRUMENT.operations], function_status: "own", match_type: "fixed_operational_instrument" }
  };
}
