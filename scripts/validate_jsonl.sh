#!/usr/bin/env bash
set -euo pipefail
python3 src/validation/validate_jsonl.py --jsonl tmp/build/ordbokene.jsonl --report debug/export/validation_report.json
