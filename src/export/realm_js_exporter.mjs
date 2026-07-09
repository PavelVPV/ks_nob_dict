#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
let Realm;
for (const candidate of [process.env.REALM_JS_MODULE, path.resolve('tools/realm-js-runtime/node_modules/realm'), 'realm']) {
  if (!candidate) continue;
  try { Realm = require(candidate); break; } catch (_) {}
}
if (!Realm) {
  console.error('realm-js is not installed. Run ./scripts/bootstrap_realm_js.sh or set REALM_JS_MODULE.');
  process.exit(2);
}

const args = new Map();
for (let i = 2; i < process.argv.length; i += 2) args.set(process.argv[i], process.argv[i + 1]);
const realmPath = args.get('--realm');
const outPath = args.get('--out');
const sample = Number(args.get('--sample') || 0);
if (!realmPath || !outPath) throw new Error('Usage: realm_js_exporter.mjs --realm PATH --out PATH [--sample N]');

function values(obj, key) {
  try {
    const v = obj?.[key];
    if (!v) return [];
    if (typeof v.filtered === 'function' || typeof v.length === 'number') return Array.from(v);
    return Array.isArray(v) ? v : [v];
  } catch { return []; }
}
function text(obj, keys) {
  for (const k of keys) {
    try { const v = obj?.[k]; if (typeof v === 'string' && v.trim()) return v.trim(); } catch {}
  }
  return '';
}
function collectText(obj, preferred, depth = 0, seen = new Set()) {
  if (!obj || depth > 5 || seen.has(obj)) return [];
  seen.add(obj);
  const out = [];
  for (const k of preferred) {
    const t = text(obj, [k]);
    if (t) out.push(t);
  }
  for (const key of ['entries', 'children', 'childGroups', 'senseGroups', 'senses', 'definitions']) {
    for (const child of values(obj, key)) out.push(...collectText(child, preferred, depth + 1, seen));
  }
  return [...new Set(out)].filter(Boolean);
}
function firstHeadword(entry) {
  const direct = text(entry, ['headword', 'lemma', 'word', 'title']);
  if (direct) return direct;
  for (const child of values(entry, 'headwords')) {
    const t = text(child, ['headword', 'lemma', 'word', 'text', 'value']);
    if (t) return t;
  }
  return '';
}
function stringsFromList(entry, listName, keys) {
  const out = [];
  for (const child of values(entry, listName)) {
    const t = text(child, keys);
    if (t) out.push(t);
  }
  return [...new Set(out)];
}

const realm = new Realm({ path: realmPath, readOnly: true });
const classNames = realm.schema.map(s => s.name);
const entryClass = classNames.includes('WordEntry') ? 'WordEntry' : classNames.find(n => /entry|article|word/i.test(n));
if (!entryClass) throw new Error(`Could not identify entry class from schema: ${classNames.join(', ')}`);
const rows = realm.objects(entryClass);
fs.mkdirSync(path.dirname(outPath), { recursive: true });
const out = fs.createWriteStream(outPath, { encoding: 'utf8' });
let written = 0, skipped = 0;
for (const entry of rows) {
  const headword = firstHeadword(entry);
  if (!headword) { skipped++; continue; }
  const definitions = collectText(entry, ['definition', 'meaning', 'flattenedNodeText', 'bodyText']);
  const rec = {
    id: text(entry, ['id', '_id', 'entryId']) || `${entryClass}-${written + 1}`,
    language: text(entry, ['language', 'lang']) || 'nb/nn',
    headword,
    part_of_speech: stringsFromList(entry, 'grams', ['full', 'abbreviated', 'name']).join('; '),
    definitions,
    examples: collectText(entry, ['example', 'exampleText']),
    inflections: stringsFromList(entry, 'inflections', ['inflectionText', 'inflection', 'text', 'value']),
    etymology: collectText(entry, ['etymology', 'etymologyText']).join('\n'),
    references: stringsFromList(entry, 'references', ['target', 'headword', 'text', 'value'])
  };
  out.write(JSON.stringify(rec) + '\n');
  written++;
  if (sample && written >= sample) break;
}
out.end();
realm.close();
console.log(JSON.stringify({ mode: 'realm-js', entryClass, schemaClasses: classNames.length, records: written, skipped, out: outPath }, null, 2));
