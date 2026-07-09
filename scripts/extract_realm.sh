#!/usr/bin/env bash
set -euo pipefail
apk=$(./scripts/extract_apk.sh)
mkdir -p tmp/build/realm
unzip -p "$apk" assets/database/ordboken.realm_109nn_88nb.zip > tmp/build/realm.zip
unzip -o tmp/build/realm.zip -d tmp/build/realm >/dev/null
echo tmp/build/realm/ordboken.realm
