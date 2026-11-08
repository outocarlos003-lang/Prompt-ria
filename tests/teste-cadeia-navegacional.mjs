import fs from "node:fs";
import path from "node:path";
import assert from "node:assert/strict";

const root = process.cwd();
const base = path.join(root, "Promptária");
const manifest = JSON.parse(fs.readFileSync(path.join(base, "manifest.json"), "utf8"));
const instruments = manifest.instruments;
const errors = [];
const fail = (message) => errors.push(message);
const exists = (relative) => fs.existsSync(path.join(root, relative));
const byPath = new Map(instruments.map((item) => [item.path, item]));
const normalize = (value) => String(value ?? "")
  .replace(/<[^>]*>/g, "")
  .replace(/&amp;/g, "&")
  .replace(/&quot;/g, '"')
  .replace(/&#39;/g, "'")
  .replace(/&nbsp;/g, " ")
  .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
  .toLocaleLowerCase("pt-BR").replace(/[^\p{L}\p{N}]+/gu, " ").trim().replace(/\s+/g, " ");

assert.ok(Array.isArray(instruments) && instruments.length > 0,
  "manifest.instruments deve conter pelo menos um instrumento");

for (const item of instruments) {
  if (!item.path || !exists(item.path)) {
    fail(`${item.id ?? "(sem ID)"}: arquivo físico ausente: ${item.path}`);
    continue;
  }

  if (item.entry !== item.path) fail(`${item.id}: entry diverge de path`);
  if (item.canonical_reference?.id !== item.id) fail(`${item.id}: ID canônico divergente`);
  if (item.canonical_reference?.path !== item.path) fail(`${item.id}: caminho canônico divergente`);
  if (item.canonical_reference?.title !== item.title) fail(`${item.id}: título canônico divergente`);

  for (const relation of ["previous", "next"]) {
    const target = byPath.get(item[relation]);
    if (!target) {
      fail(`${item.id}: ${relation} aponta para instrumento inexistente: ${item[relation]}`);
      continue;
    }

    const inverse = relation === "next" ? "previous" : "next";
    if (target[inverse] !== item.path) fail(`${item.id}: ${relation} não recíproco com ${target.id}`);
  }

  const content = fs.readFileSync(path.join(root, item.path), "utf8");
  if (/\.md$/i.test(item.path)) {
    const markdownTitle = content.match(/^#\s+(.+)$/m)?.[1];
    if (!markdownTitle) fail(`${item.id}: título Markdown ausente`);
    else if (normalize(markdownTitle) !== normalize(item.title)) {
      fail(`${item.id}: título Markdown difere do manifesto`);
    }
  } else if (/\.html?$/i.test(item.path)) {
    const h1 = content.match(/<h1\b[^>]*>([\s\S]*?)<\/h1>/i)?.[1];
    const htmlTitle = h1 ?? content.match(/<title\b[^>]*>([\s\S]*?)<\/title>/i)?.[1];
    if (!htmlTitle) fail(`${item.id}: HTML sem h1/title verificável`);
    else if (normalize(htmlTitle) !== normalize(item.title)) {
      fail(`${item.id}: título HTML difere do manifesto (HTML="${normalize(htmlTitle)}"; manifesto="${normalize(item.title)}")`);
    }
  } else fail(`${item.id}: extensão canônica não suportada: ${item.path}`);
}

// Confirm that next traverses one connected cycle containing every catalogued instrument.
const start = instruments[0];
const visited = new Set();
let cursor = start;
while (cursor && !visited.has(cursor.path)) {
  visited.add(cursor.path);
  cursor = byPath.get(cursor.next);
}

if (cursor?.path !== start.path) fail("next não forma um ciclo único que retorna ao primeiro instrumento");
if (visited.size !== instruments.length) {
  const missing = instruments.filter((item) => !visited.has(item.path)).map((item) => item.id);
  fail("cadeia desconectada; instrumentos não visitados: " + missing.join(", "));
}

// Compare the sitemap with the exact set of catalogued paths plus the root page.
const sitemapPath = path.join(base, "sitemap.xml");
if (!fs.existsSync(sitemapPath)) {
  fail("sitemap.xml ausente");
} else {
  const sitemap = fs.readFileSync(sitemapPath, "utf8");
  const listed = [...sitemap.matchAll(/<loc>([\s\S]*?)<\/loc>/g)].map((match) => match[1].trim());
  const siteBase = "https://outocarlos003-lang.github.io/Prompt-ria/";
  const toSitemapUrl = (relativePath) => new URL(encodeURI(relativePath), siteBase).href;
  const expected = ["Promptária/Index.html", ...instruments.map((item) => item.path)].map(toSitemapUrl);
  if (new Set(listed).size !== listed.length) fail("sitemap.xml contém URLs duplicadas");
  for (const entry of expected) if (!listed.includes(entry)) fail("sitemap.xml não contém: " + entry);
  for (const entry of listed) if (!expected.includes(entry)) fail("sitemap.xml contém URL fora do catálogo: " + entry);
  if (listed.length !== expected.length) fail(`sitemap.xml contém ${listed.length} entradas; esperado: ${expected.length}`);
  for (const entry of listed) {
    try {
      const url = new URL(entry);
      if (url.protocol !== "https:" || url.host !== "outocarlos003-lang.github.io") fail("sitemap.xml contém URL não absoluta ou host inesperado: " + entry);
    } catch { fail("sitemap.xml contém URL inválida: " + entry); }
  }
}

if (errors.length) {
  console.error("\nPROMPTÁRIA — CADEIA NAVEGACIONAL: FALHA");
  errors.forEach((error) => console.error("✖ " + error));
  process.exit(1);
}

console.log("\nPROMPTÁRIA — CADEIA NAVEGACIONAL: OK");
console.log("Instrumentos verificados:", instruments.length);
console.log("Ciclo completo, reciprocidade, HTML/manifesta/canônica e sitemap: OK");
