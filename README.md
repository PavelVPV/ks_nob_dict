# Ordbøkene APK to Kindle Dictionary

This repository contains a personal-use pipeline that reconstructs the supplied split Ordbøkene archive, extracts the bundled offline Realm database from the Android APK, exports a canonical JSONL intermediate file, validates it, generates Kindle dictionary source, and packages the final Kindle-compatible dictionary.

Do not publish or commit extracted dictionary data. The generated Realm, JSONL, Kindle source, and release dictionary are local artifacts only.

## Architecture

```text
Ordbøkene.zip.001..004
  -> tmp/build/Ordbøkene.zip
  -> tmp/build/Ordbøkene.apk
  -> tmp/build/realm/ordboken.realm
  -> tmp/build/ordbokene.jsonl
  -> dist/kindle_source/
  -> release/ordbokene-kindle.epub
```

`ordbokene-kindle.mobi` is attempted automatically when `ebook-convert` is installed. In this environment no MOBI converter is available, so the newest generated Kindle-compatible deliverable is `release/ordbokene-kindle.epub`.

## What was found in the APK

The APK contains the offline database at:

```text
assets/database/ordboken.realm_109nn_88nb.zip
```

That ZIP contains:

```text
ordboken.realm
```

The Realm file is extracted only into `tmp/build/realm/`, which is ignored by Git.

## Realm schema inspection

The schema inspection script writes reports under `debug/schema/`:

- `debug/schema/schema_summary.json`
- `debug/schema/schema_summary.md`

The committed schema summary was generated in this environment before Realm Core bindings were available, so it uses conservative Realm metadata/string inspection and documents that limitation. With `realm-js` installed, use the Realm JS exporter for full object graph traversal. The detected model classes are:

- `WordEntry`
- `Headword`
- `WordSenseGroup`
- `WordSenseEntry`
- `Inflection`
- `WordGram`
- `Etymology`
- `Reference`
- `InflectionTableRow`

Detected relationship/list-style field names include `headwords`, `senseGroups`, `childGroups`, `inflections`, `grams`, `etymology`, and `references`.

## Exporter and canonical JSONL

The canonical intermediate file is JSONL at `tmp/build/ordbokene.jsonl`. Each line has this normalized shape:

```json
{
  "id": "...",
  "language": "nb/nn",
  "headword": "...",
  "part_of_speech": "...",
  "definitions": [],
  "examples": [],
  "inflections": [],
  "etymology": "",
  "references": []
}
```

The preferred exporter is `src/export/realm_js_exporter.mjs`, which uses `realm-js` to open the Realm file read-only, discover classes dynamically, and traverse `WordEntry` objects into canonical JSONL. Run `./scripts/bootstrap_realm_js.sh` to install/build `realm-js` and its Realm Core dependency into `tools/realm-js-runtime/`. If network or native builds are blocked, `scripts/export_jsonl.sh` falls back to the conservative string-probe exporter so the rest of the pipeline remains testable. A Kotlin `DynamicRealm` exporter stub is retained as an additional reference for JVM/Android Realm environments.

## Validation

`src/validation/validate_jsonl.py` checks:

- duplicate IDs
- duplicate headwords
- missing definitions
- malformed JSONL records

The report is written to `debug/export/validation_report.json` and is ignored by Git.

## Kindle generation

`src/kindle/generate_source.py` reads only JSONL. It does not depend on Realm. It generates:

- XHTML entries with Mobipocket `idx:entry` / `idx:orth` lookup markup
- OPF dictionary metadata with `DictionaryInLanguage` and `DictionaryOutLanguage`
- EPUB container files

The release builder packages `release/ordbokene-kindle.epub`. If Calibre's `ebook-convert` is available, it also attempts `release/ordbokene-kindle.mobi`.

## Full rebuild

Run:

```bash
./scripts/build_dictionary.sh
```

For a miniature test build:

```bash
./scripts/build_dictionary.sh --sample 100
```

To install or build Realm JS/Core locally before exporting:

```bash
./scripts/bootstrap_realm_js.sh
```

Individual stages are also available:

```bash
./scripts/reconstruct.sh
./scripts/extract_apk.sh
./scripts/extract_realm.sh
./scripts/inspect_schema.sh
./scripts/export_jsonl.sh
./scripts/validate_jsonl.sh
./scripts/generate_kindle_source.sh
```

## Troubleshooting

- If `ordbokene-kindle.mobi` is not produced, install Calibre or Amazon Kindle tooling and rerun `./scripts/build_dictionary.sh`.
- If `./scripts/bootstrap_realm_js.sh` fails with a proxy or registry error, install `realm` manually in `tools/realm-js-runtime/` or set `REALM_JS_MODULE` to an existing Realm JS module path, then rerun `./scripts/build_dictionary.sh`.
- If a richer definition export is required beyond Realm JS heuristics, run the Kotlin `DynamicRealm` approach in an environment with Realm Java/Core available, then keep the downstream JSONL-to-Kindle pipeline unchanged.
- Never commit `tmp/`, `dist/`, `release/`, `*.realm`, `*.json`, or `*.jsonl` outputs.

## Kindle Scribe installation

1. Use the final file in `release/`.
2. Prefer `ordbokene-kindle.mobi` if your local toolchain produced it; otherwise use `ordbokene-kindle.epub`.
3. Transfer it with Amazon Send to Kindle or USB, depending on which format your Kindle/account accepts.
4. On the Kindle Scribe, open language/dictionary settings and select the installed Norwegian dictionary for lookup.
