/**
 * Promptária — resolvedor determinístico de correferência funcional.
 *
 * Ordem de decisão:
 *   ID > título canônico exato > título normalizado > alias > capacidade.
 * Correspondências ambíguas nunca são ativadas silenciosamente.
 */

export const MATCH_TYPES = Object.freeze({
  ID: "id",
  EXACT_TITLE: "exact_title",
  NORMALIZED_TITLE: "normalized_title",
  ALIAS: "alias",
  CAPABILITY: "capability",
  INVALID_IDENTITY: "invalid_identity",
  AMBIGUOUS: "ambiguous",
  NONE: "none"
});

export const normalize = (value) => String(value ?? "")
  .normalize("NFD")
  .replace(/[\u0300-\u036f]/g, "")
  .toLocaleLowerCase()
  .replace(/[^a-z0-9]+/g, " ")
  .trim();

const unique = (values) => [...new Set(values.filter(Boolean))];

export function buildReferenceIndex(instruments = []) {
  const byId = new Map();
  const byExactTitle = new Map();
  const byNormalizedTitle = new Map();
  const byAlias = new Map();
  const byCapability = new Map();

  for (const instrument of instruments) {
    if (!instrument?.id || !instrument?.title) continue;
    byId.set(String(instrument.id), instrument);
    byExactTitle.set(String(instrument.title).trim(), instrument);

    const nt = normalize(instrument.title);
    if (nt) {
      const list = byNormalizedTitle.get(nt) || [];
      list.push(instrument);
      byNormalizedTitle.set(nt, list);
    }

    for (const alias of unique(instrument.aliases || [])) {
      const key = normalize(alias);
      if (!key) continue;
      const list = byAlias.get(key) || [];
      if (!list.some(x => x.id === instrument.id)) list.push(instrument);
      byAlias.set(key, list);
    }

    for (const capability of unique(instrument.capabilities || [])) {
      const key = normalize(capability);
      if (!key) continue;
      const list = byCapability.get(key) || [];
      if (!list.some(x => x.id === instrument.id)) list.push(instrument);
      byCapability.set(key, list);
    }
  }

  return { byId, byExactTitle, byNormalizedTitle, byAlias, byCapability };
}

const result = (instrument, matchType, confidence, mention, candidates = []) => ({
  mention,
  instrument_id: instrument?.id ?? null,
  canonical_title: instrument?.title ?? null,
  path: instrument?.path ?? null,
  match_type: matchType,
  confidence,
  activation: Boolean(instrument) && matchType !== MATCH_TYPES.CAPABILITY,
  candidates: candidates.map(x => x.id)
});

export function resolveReference(text, index) {
  const mention = String(text ?? "").trim();
  if (!mention) return result(null, MATCH_TYPES.NONE, 0, mention);

  const exactId = index.byId.get(mention);
  if (exactId) return result(exactId, MATCH_TYPES.ID, 1, mention);

  const exactTitle = index.byExactTitle.get(mention);
  if (exactTitle) return result(exactTitle, MATCH_TYPES.EXACT_TITLE, 1, mention);

  const normalized = normalize(mention);
  const normalizedTitles = index.byNormalizedTitle.get(normalized) || [];
  if (normalizedTitles.length === 1)
    return result(normalizedTitles[0], MATCH_TYPES.NORMALIZED_TITLE, 0.99, mention);

  const aliases = index.byAlias.get(normalized) || [];
  if (aliases.length === 1)
    return result(aliases[0], MATCH_TYPES.ALIAS, 0.97, mention);
  if (aliases.length > 1)
    return { ...result(null, MATCH_TYPES.AMBIGUOUS, 0, mention, aliases), activation: false };

  const capabilities = index.byCapability.get(normalized) || [];
  if (capabilities.length)
    return { ...result(null, MATCH_TYPES.CAPABILITY, 0.5, mention, capabilities), activation: false, candidates: capabilities.map(x => x.id) };

  return result(null, MATCH_TYPES.NONE, 0, mention);
}

export function resolveMentions(text, instruments, index = buildReferenceIndex(instruments)) {
  const source = String(text ?? "");
  const candidates = [];

  for (const instrument of instruments || []) {
    const terms = unique([
      instrument.id,
      instrument.title,
      ...(instrument.aliases || []),
      ...(instrument.capabilities || [])
    ]).sort((a, b) => String(b).length - String(a).length);

    for (const term of terms) {
      if (!term) continue;
      const re = new RegExp(escapeRegExp(String(term)), "giu");
      let match;
      while ((match = re.exec(source))) {
        const resolved = resolveReference(match[0], index);
        if (resolved.instrument_id === instrument.id) {
          candidates.push({ ...resolved, start: match.index, end: match.index + match[0].length });
        }
      }
    }
  }

  const deduped = new Map();
  for (const item of candidates) {
    const key = item.start + ":" + item.end + ":" + item.instrument_id;
    const current = deduped.get(key);
    if (!current || item.confidence > current.confidence) deduped.set(key, item);
  }

  return [...deduped.values()]
    .sort((a, b) => a.start - b.start || b.confidence - a.confidence)
    .filter((item, i, all) => i === 0 || item.start >= all[i - 1].end || item.instrument_id !== all[i - 1].instrument_id);
}

export function validateReferenceIndex(instruments = []) {
  const errors = [];
  const seenAliases = new Map();

  for (const instrument of instruments) {
    const local = new Set();
    for (const alias of instrument.aliases || []) {
      const key = normalize(alias);
      if (!key) {
        errors.push(`${instrument.id}: alias vazio após normalização`);
        continue;
      }
      if (local.has(key)) errors.push(`${instrument.id}: alias duplicado: ${alias}`);
      local.add(key);
      const owners = seenAliases.get(key) || [];
      if (!owners.includes(instrument.id)) owners.push(instrument.id);
      seenAliases.set(key, owners);
    }
  }

  for (const [alias, owners] of seenAliases) {
    if (owners.length > 1)
      errors.push(`alias ambíguo entre instrumentos: "${alias}" -> ${owners.join(", ")}`);
  }

  return errors;
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^\${}()|[\]\\]/g, "\\$&");
}


export function verifyInstrumentIdentity(instrument, content) {
  if (!instrument?.id || !instrument?.title || !instrument?.path) {
    return { verified: false, status: MATCH_TYPES.INVALID_IDENTITY, reason: "canonical_identity_incomplete" };
  }
  const html = String(content ?? "");
  const match = html.match(/<title>[ \t\r\n]*(.*?)[ \t\r\n]*<\/title>/is);
  const physicalTitle = match ? match[1].replace(/&amp;/g, "&").trim() : null;
  const verified = Boolean(physicalTitle && normalize(physicalTitle) === normalize(instrument.title));
  return {
    verified,
    status: verified ? "verified" : MATCH_TYPES.INVALID_IDENTITY,
    id: instrument.id,
    canonical_title: instrument.title,
    path: instrument.path,
    physical_title: physicalTitle,
    reason: verified ? "canonical_id_title_path_content_title_match" : "content_title_mismatch_or_missing"
  };
}
