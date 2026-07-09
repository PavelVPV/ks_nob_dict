#!/usr/bin/env bash
set -euo pipefail
./scripts/reconstruct.sh >/dev/null
unzip -o tmp/build/Ordbøkene.zip -d tmp/build >/dev/null
echo tmp/build/Ordbøkene.apk
