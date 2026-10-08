/**
 * Promptária — resolvedor determinístico de correferência funcional v3.
 * Título existente + menção genérica + ausência de exceção => correferência,
 * função própria e acionamento. Múltiplos títulos coexistem.
 */
export const MATCH_TYPES = Object.freeze({
  ID: "id",
  EXACT_TITLE: "exact_title",
  NORMALIZED_TITLE: "normalized_title",
  ALIAS_HINT: "alias_hint",
  AMBIGUOUS: "ambiguous",
  NONE: "none"
});

export const FUNCTION_STATUS = Object.freeze({
  OWN: "propria_preservada",
  DIVERSE: "diversa_explicitamente_atribuida"
});

export const ARCHITECTURE_POLICY = Object.freeze({
  version: "3.0",
  sections: Object.freeze([
    "I. TÍTULO, CORREFERÊNCIA E IDENTIDADE",
    "II. DEMANDA, CONTEXTO, PARAMETRIZAÇÃO E ADAPTAÇÃO",
    "III. FUNÇÃO PRÓPRIA E FUNÇÃO DIVERSA",
    "IV. RECUPERAÇÃO, ACIONAMENTO E EXECUÇÃO",
    "V. ACIONAMENTO COORDENADO",
    "VI. INSTRUMENTOS ADICIONAIS E FIXO",
    "VII. MÚLTIPLOS TÍTULOS",
    "VIII. FUNÇÃO DIVERSA EM MÚLTIPLOS TÍTULOS",
    "IX. RESPONSABILIDADE E NÃO SUBSTITUIÇÃO",
    "X. ORIGEM, DESTINO E MULTIDIRETÓRIO",
    "XI. EXECUÇÃO, MATERIALIZAÇÃO E RESULTADOS",
    "XII. COMPATIBILIZAÇÃO",
    "XIII. VALIDAÇÃO E RASTREABILIDADE",
    "XIV. REUTILIZAÇÃO E PRESERVAÇÃO",
    "XV. SEQUÊNCIAS ARQUITETURAIS",
    "XVI. PRINCÍPIO DA NÃO SUBSTITUIÇÃO",
    "XVII. REGRA OPERACIONAL FINAL",
    "XVIII. SÍNTESE AFORÍSTICA",
    "XIX. PRINCÍPIO CONCLUSIVO"
  ]),
  titleActivates: true,
  genericMentionPreservesOwnFunction: true,
  diverseFunctionIsException: true,
  ambiguityFavorsOwnFunction: true,
  silenceIsNotNegation: true,
  aliasesDoNotReplaceTitle: true,
  capabilitiesDoNotReplaceTitle: true,
  multipleTitlesAreCumulative: true,
  multipleTitlesAreNonExclusive: true,
  exceptionIsLocalToOccurrence: true,
  coordinatorDoesNotFuse: true,
  repositoryPreservesContent: true,
  githubRecoversContent: true,
  contentDeterminesIdentity: true,
  contextualizationDoesNotChangeIdentity: true,
  parameterizationDoesNotReplaceLogic: true,
  adaptationDoesNotChangeIdentity: true,
  destinationNocturnaIsNotDefault: true,
  ambiguousDestinationBlocksDependentMaterialization: true,
  traceabilityRequired: true,
  githubActionsRequiresTransmittedRequest: true
});

export const normalize = (value) => String(value ?? "")
  .normalize("NFKC")
  .normalize("NFD")
  .replace(/[\u0300-\u036f]/g, "")
  .toLocaleLowerCase()
  .replace(/[^a-z0-9]+/g, " ")
  .trim()
  .replace(/\s+/g, " ");

const unique = (values) => [...new Set((values || []).filter(Boolean).map(String))];

export function buildReferenceIndex(instruments = []) {
  const byId = new Map();
  const byExactTitle = new Map();
  const byNormalizedTitle = new Map();
  const byAlias = new Map();

  for (const instrument of instruments) {
    if (!instrument?.id || !instrument?.title) continue;
    const id = String(instrument.id);
    const title = String(instrument.title).trim();
    byId.set(id, instrument);
    byExactTitle.set(title, instrument);

    const nt = normalize(title);
    if (nt) {
      const list = byNormalizedTitle.get(nt) || [];
      if (!list.some(x => x.id === id)) list.push(instrument);
      byNormalizedTitle.set(nt, list);
    }

    for (const alias of unique(instrument.aliases)) {
      const key = normalize(alias);
      if (!key || key === nt) continue;
      const list = byAlias.get(key) || [];
      if (!list.some(x => x.id === id)) list.push(instrument);
      byAlias.set(key, list);
    }
  }
  return { byId, byExactTitle, byNormalizedTitle, byAlias };
}

const baseResult = (mention, overrides = {}) => ({
  mention,
  instrument_id: null,
  canonical_title: null,
  path: null,
  match_type: MATCH_TYPES.NONE,
  confidence: 0,
  activation: false,
  correferencia: false,
  function_status: FUNCTION_STATUS.OWN,
  exception_scope: null,
  candidates: [],
  ...overrides
});

export function resolveReference(text, index) {
  const mention = String(text ?? "").trim();
  if (!mention) return baseResult(mention);

  const exactId = index?.byId?.get(mention);
  if (exactId) return baseResult(mention, {
    instrument_id: exactId.id, canonical_title: exactId.title, path: exactId.path ?? null,
    match_type: MATCH_TYPES.ID, confidence: 1, activation: true, correferencia: true
  });

  const exactTitle = index?.byExactTitle?.get(mention);
  if (exactTitle) return baseResult(mention, {
    instrument_id: exactTitle.id, canonical_title: exactTitle.title, path: exactTitle.path ?? null,
    match_type: MATCH_TYPES.EXACT_TITLE, confidence: 1, activation: true, correferencia: true
  });

  const normalized = normalize(mention);
  const normalizedTitles = index?.byNormalizedTitle?.get(normalized) || [];
  if (normalizedTitles.length === 1) {
    const instrument = normalizedTitles[0];
    return baseResult(mention, {
      instrument_id: instrument.id, canonical_title: instrument.title, path: instrument.path ?? null,
      match_type: MATCH_TYPES.NORMALIZED_TITLE, confidence: 0.99, activation: true, correferencia: true
    });
  }
  if (normalizedTitles.length > 1) {
    return baseResult(mention, {
      match_type: MATCH_TYPES.AMBIGUOUS, candidates: normalizedTitles.map(x => x.id)
    });
  }

  // Aliases são apenas pistas de navegação; não substituem um título para acionamento.
  const aliases = index?.byAlias?.get(normalized) || [];
  if (aliases.length) {
    return baseResult(mention, {
      match_type: aliases.length === 1 ? MATCH_TYPES.ALIAS_HINT : MATCH_TYPES.AMBIGUOUS,
      confidence: aliases.length === 1 ? 0.5 : 0,
      candidates: aliases.map(x => x.id)
    });
  }
  return baseResult(mention);
}

const DIVERSE_PATTERNS = [
  /\b(?:como|na função de|no papel de|com a finalidade de|com o objetivo de)\b.{0,180}\b(?:outra|diversa|diferente)\s+(?:função|finalidade|papel)\b/i,
  /\b(?:outra|diversa|diferente)\s+(?:função|finalidade|papel)\b.{0,180}\b(?:para|do|da|de)\b/i,
  /\b(?:substitua|substituir|substituto|substituta)\b.{0,180}\b(?:função|finalidade|papel)\b/i,
  /\b(?:não|nao)\s+(?:use|utilize|empregue|aplique|acione)\b.{0,180}\b(?:função|finalidade|papel)\s+(?:própria|propria|original)\b/i,
  /\b(?:deve|deverá|devera)\b.{0,100}\b(?:atuar|desempenhar|funcionar)\b.{0,120}\b(?:como|para)\b/i
];

export function classifyFunction(context) {
  const source = String(context ?? "").trim();
  if (!source) return { status: FUNCTION_STATUS.OWN, reason: "silêncio não é negação" };
  for (const pattern of DIVERSE_PATTERNS) {
    if (pattern.test(source)) {
      return {
        status: FUNCTION_STATUS.DIVERSE,
        reason: "atribuição funcional diversa expressa ou inequivocamente determinada",
        exception_scope: "occurrence"
      };
    }
  }
  return {
    status: FUNCTION_STATUS.OWN,
    reason: "menção genérica, compatível ou contexto insuficiente"
  };
}

function normalizeWithOrigins(value) {
  const chars = [];
  const origins = [];
  const input = String(value ?? "");
  for (let i = 0; i < input.length; i++) {
    const chunk = input[i].normalize("NFKC").normalize("NFD")
      .replace(/[\\u0300-\\u036f]/g, "").toLocaleLowerCase();
    for (const char of chunk) {
      const normalized = /[a-z0-9]/i.test(char) ? char : " ";
      chars.push(normalized);
      origins.push(i);
    }
  }

  const out = [];
  const outOrigins = [];
  let pendingSpace = false;
  let pendingOrigin = 0;
  for (let i = 0; i < chars.length; i++) {
    const char = chars[i];
    if (char === " ") {
      if (out.length) {
        pendingSpace = true;
        pendingOrigin = origins[i];
      }
      continue;
    }
    if (pendingSpace) {
      out.push(" ");
      outOrigins.push(pendingOrigin);
      pendingSpace = false;
    }
    out.push(char);
    outOrigins.push(origins[i]);
  }
  return { text: out.join(" "), origins: outOrigins };
}

function localContext(text, start, end) {
  const radius = 480;
  const left = Math.max(0, start - radius);
  const right = Math.min(text.length, end + radius);
  const window = text.slice(left, right);
  const relStart = start - left;
  const relEnd = end - left;
  const separators = [...window.matchAll(/(?:[.!?;]|\n\s*\n)/g)];
  let begin = 0, finish = window.length;
  for (const s of separators) {
    if (s.index + s[0].length <= relStart) begin = s.index + s[0].length;
    if (s.index >= relEnd) { finish = s.index; break; }
  }
  return window.slice(begin, finish).trim();
}

export function resolveMentions(text, instruments, index = buildReferenceIndex(instruments)) {
  const source = String(text ?? "");
  const normalizedSource = normalizeWithOrigins(source);
  const candidates = [];

  for (const instrument of instruments || []) {
    if (!instrument?.title) continue;
    const needle = normalize(instrument.title);
    if (!needle) continue;
    const re = new RegExp(escapeRegExp(needle).replace(/\\ /g, "\\s+"), "giu");
    let match;
    while ((match = re.exec(normalizedSource.text))) {
      const nStart = match.index;
      const nEnd = match.index + match[0].length;
      const originalStart = normalizedSource.origins[nStart];
      const originalEnd = normalizedSource.origins[nEnd - 1] + 1;
      const resolved = resolveReference(instrument.title, index);
      if (resolved.instrument_id !== instrument.id) continue;

      const context = localContext(source, originalStart, originalEnd);
      const classification = classifyFunction(context);
      candidates.push({
        ...resolved,
        mention: source.slice(originalStart, originalEnd),
        start: originalStart,
        end: originalEnd,
        context,
        function_status: classification.status,
        exception_scope: classification.exception_scope ?? null,
        activation: classification.status === FUNCTION_STATUS.OWN,
        action: classification.status === FUNCTION_STATUS.OWN
          ? "acionar_função_própria"
          : "não_acionar_função_própria_nesta_ocorrência"
      });
    }
  }

  const deduped = new Map();
  for (const item of candidates) {
    const key = [item.start, item.end, item.instrument_id].join(":");
    if (!deduped.has(key)) deduped.set(key, item);
  }
  return [...deduped.values()]
    .sort((a, b) => a.start - b.start || a.instrument_id.localeCompare(b.instrument_id));
}

export function validateReferenceIndex(instruments = []) {
  const errors = [];
  const seenIds = new Set();
  const seenTitles = new Set();
  const seenAliases = new Map();

  for (const instrument of instruments) {
    if (!instrument?.id) errors.push("instrumento sem id");
    if (!instrument?.title) errors.push("instrumento sem título");
    if (!instrument?.path) errors.push((instrument?.id || "<sem-id>") + ": instrumento sem path");

    const id = String(instrument?.id ?? "");
    const title = normalize(instrument?.title ?? "");
    if (id && seenIds.has(id)) errors.push("id duplicado: " + id);
    if (id) seenIds.add(id);
    if (title && seenTitles.has(title)) errors.push("título duplicado: " + instrument.title);
    if (title) seenTitles.add(title);

    for (const alias of unique(instrument.aliases)) {
      const key = normalize(alias);
      if (!key) errors.push(id + ": alias vazio após normalização");
      const owners = seenAliases.get(key) || [];
      if (!owners.includes(id)) owners.push(id);
      seenAliases.set(key, owners);
    }
  }

  // Aliases podem ser compartilhados: são apenas pistas não acionantes.
  // A ambiguidade relevante para acionamento é a do título canônico.
  return errors;
}

export function buildTraceability(matches = [], request = {}) {
  return matches.map(match => ({
    título: match.canonical_title,
    instrumento: match.instrument_id,
    correferência: match.correferencia,
    função: match.function_status,
    acionamento: match.activation,
    exceção: match.exception_scope,
    contexto: match.context,
    relação_com_demais: request.multiple_titles
      ? "mútua, cumulativa, coordenada, simultânea, individual e não exclusiva"
      : "individual",
    origem: request.origin ?? null,
    destino: request.destination ?? null,
    parâmetros: request.parameters ?? {},
    ação: match.action,
    resultado: request.result ?? null,
    validação: request.validation ?? null
  }));
}

function escapeRegExp(value) {
  return String(value).replace(/[.*+?^\$()|[\]\\]/g, "\\$&");
}
