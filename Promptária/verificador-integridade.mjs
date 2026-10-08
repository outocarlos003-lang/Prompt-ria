import fs from "node:fs";
import path from "node:path";
import { buildReferenceIndex, validateReferenceIndex } from "./resolver-correferencia.mjs";

const ROOT=process.cwd();
const manifestPath=path.join(ROOT,"Promptária","manifest.json");
const sitemapPath=path.join(ROOT,"Promptária","sitemap.xml");
const manifest=JSON.parse(fs.readFileSync(manifestPath,"utf8"));
const errors=[],warnings=[];
const instruments=manifest.instruments||[];
const fail=(m)=>errors.push(m);
const warn=(m)=>warnings.push(m);
const exists=(p)=>fs.existsSync(path.join(ROOT,p));
const unique=(xs,label)=>{const seen=new Set();for(const x of xs){if(seen.has(x))fail(label+" duplicado: "+x);seen.add(x)}};

if(manifest.schema_version!=="2.0") fail("schema_version inesperado");
if(!Array.isArray(instruments)||!instruments.length) fail("manifest.instruments vazio ou inválido");

unique(instruments.map(x=>x.id),"id");
unique(instruments.map(x=>x.title),"título");
unique(instruments.map(x=>x.path),"path");

const referenceIndex=buildReferenceIndex(instruments);
const referenceErrors=validateReferenceIndex(instruments);
referenceErrors.forEach(fail);

for(const x of instruments){
  if(!x.id||!x.title||!x.path) fail("instrumento incompleto: "+JSON.stringify(x));
  if(x.node_type!=="instrument") fail(x.id+": node_type inválido");
  if(!x.canonical_reference||x.canonical_reference.id!==x.id||x.canonical_reference.path!==x.path||x.canonical_reference.title!==x.title)
    fail(x.id+": canonical_reference divergente");
  if(!Array.isArray(x.aliases)||!x.aliases.length) fail(x.id+": sem aliases");
  if(!Array.isArray(x.capabilities)||!x.capabilities.length) fail(x.id+": sem capabilities");
  if(!exists(x.path)) fail(x.id+": arquivo não existe: "+x.path);
  for(const rel of ["previous","next","entry"]){
    if(!x[rel]) fail(x.id+": "+rel+" ausente");
    else if(!instruments.some(y=>y.path===x[rel])) fail(x.id+": "+rel+" aponta para nó inexistente: "+x[rel]);
  }
}
for(const x of instruments){
  const p=instruments.find(y=>y.path===x.next);
  const n=instruments.find(y=>y.path===x.previous);
  if(p&&p.previous!==x.path) fail(x.id+": next não possui previous recíproco");
  if(n&&n.next!==x.path) fail(x.id+": previous não possui next recíproco");
  if(x.entry!==x.path) fail(x.id+": entry divergente do path");
}
const pages=fs.readdirSync(path.join(ROOT,"Promptária"),{withFileTypes:true})
  .filter(d=>d.isDirectory()).map(d=>path.join("Promptária",d.name,"Index.html"))
  .filter(exists);
for(const p of pages) if(!instruments.some(x=>x.path===p)) fail("página de instrumento órfã no catálogo: "+p);
for(const x of instruments){
  const html=fs.readFileSync(path.join(ROOT,x.path),"utf8");
  if(!html.includes("navegacao-neural.js")) fail(x.id+": camada navegacional ausente");
}
for(const p of ["index.html","Promptária/Index.html","Promptária/navegacao-neural.js","Promptária/manifest.json","Promptária/rastreabilidade-producao.json","Promptária/README.md","Promptária/sitemap.xml"])
  if(!exists(p)) fail("artefato estrutural ausente: "+p);

if(exists(sitemapPath)){
  const sitemap=fs.readFileSync(sitemapPath,"utf8");
  const listed=[...sitemap.matchAll(/<loc>(.*?)<\/loc>/g)].map(m=>m[1].trim());
  const expected=["Promptária/Index.html",...instruments.map(x=>x.path)];
  unique(listed,"URL no sitemap");
  for(const p of expected) if(!listed.includes(p)) fail("sitemap sem: "+p);
  for(const p of listed) if(!expected.includes(p)) warn("sitemap contém entrada fora do catálogo: "+p);
}

const trace=JSON.parse(fs.readFileSync(path.join(ROOT,"Promptária","rastreabilidade-producao.json"),"utf8"));
if(!trace.production_chain?.length) fail("rastreabilidade sem production_chain");
if(!trace.navigation_invariants?.length) fail("rastreabilidade sem navigation_invariants");

if(errors.length){
  console.error("\nPROMPTÁRIA — INTEGRIDADE: FALHA");
  errors.forEach(e=>console.error("✖ "+e));
  if(warnings.length) warnings.forEach(w=>console.warn("⚠ "+w));
  process.exit(1);
}
console.log("\nPROMPTÁRIA — INTEGRIDADE: OK");
console.log("Instrumentos:",instruments.length);
console.log("Páginas catalogadas:",pages.length);
console.log("Sitemap verificado: sim");
console.log("Correferência semântica: "+(manifest.semantic_cross_reference?"sim":"não"));
console.log("Resolvedor determinístico: "+(manifest.semantic_cross_reference?.runtime_resolver||"ausente"));
console.log("Política de ambiguidade: "+(manifest.semantic_cross_reference?.ambiguity_policy||"ausente"));
if(warnings.length) warnings.forEach(w=>console.warn("⚠ "+w));
