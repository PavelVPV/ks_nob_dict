#!/usr/bin/env bash
set -euo pipefail
sample=0
if [[ ${1:-} == "--sample" ]]; then sample=${2:?}; fi
./scripts/inspect_schema.sh
./scripts/export_jsonl.sh ${sample:+--sample "$sample"}
./scripts/validate_jsonl.sh
./scripts/generate_kindle_source.sh
mkdir -p release
rm -f release/ordbokene-kindle.epub release/ordbokene-kindle.mobi
cd dist/kindle_source
printf 'application/epub+zip' > mimetype
zip -X0 ../../release/ordbokene-kindle.epub mimetype >/dev/null
zip -Xr9D ../../release/ordbokene-kindle.epub META-INF OEBPS >/dev/null
cd ../..
if command -v ebook-convert >/dev/null 2>&1; then ebook-convert release/ordbokene-kindle.epub release/ordbokene-kindle.mobi || true; fi
if [[ -f release/ordbokene-kindle.mobi ]]; then echo release/ordbokene-kindle.mobi; else echo release/ordbokene-kindle.epub; fi
