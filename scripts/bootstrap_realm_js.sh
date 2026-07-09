#!/usr/bin/env bash
set -euo pipefail
runtime_dir=${REALM_JS_RUNTIME_DIR:-tools/realm-js-runtime}
mkdir -p "$runtime_dir"
if [[ ! -f "$runtime_dir/package.json" ]]; then
  cat > "$runtime_dir/package.json" <<'JSON'
{"private":true,"type":"module","dependencies":{"realm":"latest"}}
JSON
fi
npm --prefix "$runtime_dir" install ${REALM_JS_BUILD_FROM_SOURCE:+--build-from-source}
node -e "const Realm=require('./${runtime_dir}/node_modules/realm'); console.log(Realm.App ? 'realm-js installed' : 'realm-js loaded')"
