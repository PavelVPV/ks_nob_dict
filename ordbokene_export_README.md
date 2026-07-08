# Ordbøkene APK → Realm → JSON → Kindle

## What was found

The APK contains:

`assets/database/ordboken.realm_109nn_88nb.zip`

Inside it is:

`ordboken.realm` — about 183.6 MB.

The Realm file is not obviously encrypted. String-level inspection finds these Realm classes:

- `WordEntry`
- `Headword`
- `WordSenseGroup`
- `WordSenseEntry`
- `Inflection`
- `WordGram`
- `Etymology`
- `Reference`
- `InflectionTableRow`

Important fields found:

- `headword`
- `definition`
- `flattenedNodeText`
- `inflectionText`
- `headwords`
- `senseGroups`
- `childGroups`
- `inflections`
- `grams`
- `etymology`

This strongly suggests the APK contains the offline dictionary data needed for a Kindle dictionary: headwords, definitions/senses, and inflected forms.

## What I could and could not do locally here

I extracted and inspected the database, but could not fully reconstruct rows directly in this environment because Realm is not SQLite and no Realm runtime/library is installed here.

The included `ordbokene_realm_string_probe.py` is a string-level probe only. It confirms content and extracts sample text, but it does not reconstruct `WordEntry -> Headword -> SenseGroup -> Inflection` relations.

The included `OrdbokeneRealmExporter.kt` is the proper next-step exporter: run it in an Android/Realm Java environment to produce structured JSON.

## Expected JSON shape

```json
[
  {
    "id": "...",
    "headwords": [{ "headword": "hus", "sortingText": "hus" }],
    "grams": [{ "full": "substantiv", "abbreviated": "s." }],
    "inflections": [{ "inflectionText": "huset" }, { "inflectionText": "husene" }],
    "senseGroups": [
      {
        "definition": "...",
        "flattenedNodeText": "...",
        "childGroups": []
      }
    ]
  }
]
```

## Kindle conversion after JSON export

After JSON exists, the conversion is straightforward:

1. For each `WordEntry`, choose the main `headword`.
2. Render article HTML from `senseGroups`, `grams`, and optionally `etymology`.
3. Add every `inflectionText` as an alternate lookup form pointing to the same article.
4. Build a Kindle dictionary via Kindle Previewer / KindleGen-compatible OPF.

## Legal note

This is suitable as a technical extraction experiment for personal use. Redistributing the extracted dictionary data or a ready-made Kindle dictionary may violate the dictionary/app license or copyright.
