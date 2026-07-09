#!/usr/bin/env bash
set -euo pipefail
sample=0
if [[ ${1:-} == "--sample" ]]; then sample=${2:?}; fi
realm=$(./scripts/extract_realm.sh)
args=(--realm "$realm" --out tmp/build/ordbokene.jsonl)
if [[ $sample -gt 0 ]]; then args+=(--sample "$sample"); fi
if node -e "require('./tools/realm-js-runtime/node_modules/realm')" >/dev/null 2>&1 || [[ -n ${REALM_JS_MODULE:-} ]]; then
  node src/export/realm_js_exporter.mjs "${args[@]}"
else
  echo "realm-js not available; using string-probe fallback. Run ./scripts/bootstrap_realm_js.sh for full Realm object export." >&2
  python3 src/export/export_realm_jsonl.py "${args[@]}"
fi
