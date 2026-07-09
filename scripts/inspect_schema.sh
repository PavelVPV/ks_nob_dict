#!/usr/bin/env bash
set -euo pipefail
realm=${1:-$(./scripts/extract_realm.sh)}
python3 src/realm/inspect_schema.py --realm "$realm" --out-dir debug/schema
