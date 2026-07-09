#!/usr/bin/env bash
set -euo pipefail
mkdir -p tmp/build
cat Ordbøkene.zip.0* > tmp/build/Ordbøkene.zip
echo tmp/build/Ordbøkene.zip
