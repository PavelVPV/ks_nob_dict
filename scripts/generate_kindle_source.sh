#!/usr/bin/env bash
set -euo pipefail
python3 src/kindle/generate_source.py --jsonl tmp/build/ordbokene.jsonl --out-dir dist/kindle_source
