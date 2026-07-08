#!/usr/bin/env python3
"""Conservative fallback exporter.

This is not the canonical Realm exporter. It exists so the pipeline can still
produce a miniature Kindle-compatible test artifact when a Realm runtime is not
available. The canonical format is JSONL and the proper exporter should use a
Realm runtime to preserve object relationships.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

WORD_RE = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿÆØÅæøå0-9][A-Za-zÀ-ÖØ-öø-ÿÆØÅæøå0-9 .,'’()\-/]{0,48}$")
BAD = {"AAAA", "T-DB", "metadata", "class", "version", "id"}
TAG_RE = re.compile(r"\|[A-Za-z]+z?|\|[KQ]\d+(?:nn|nb)?|\|[a-z]{2}")


def iter_strings(path: Path, min_len: int = 2):
    result = subprocess.run(
        ["strings", "-n", str(min_len), str(path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    for line in result.stdout.splitlines():
        yield line.strip("\x00").strip()


def clean_tagged(s: str) -> str:
    s = TAG_RE.sub(" ", s)
    s = s.replace("AAAA", " ")
    return re.sub(r"\s+", " ", s).strip(" \t|;,")


def is_word(s: str) -> bool:
    if not s or s in BAD or s.startswith("class_") or "|" in s or "AAAA" in s:
        return False
    if len(s) < 2 or len(s) > 48:
        return False
    if not WORD_RE.match(s):
        return False
    letters = sum(ch.isalpha() for ch in s)
    return letters >= max(2, len(s.replace(" ", "")) // 2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--realm", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--sample", type=int, default=0)
    args = parser.parse_args()

    realm = Path(args.realm)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    seen = set()
    words = []
    tagged_count = 0
    for s in iter_strings(realm):
        if "|" in s and len(s) > 12 and clean_tagged(s):
            tagged_count += 1
            continue
        if is_word(s):
            key = s.lower()
            if key not in seen:
                seen.add(key)
                words.append(s)
                if args.sample and len(words) >= args.sample:
                    break

    with out.open("w", encoding="utf-8") as f:
        for i, word in enumerate(words, 1):
            rec = {
                "id": f"string-probe-{i}",
                "language": "nb/nn",
                "headword": word,
                "part_of_speech": "",
                "definitions": [
                    "Lookup headword extracted from the Ordbøkene offline Realm database. Full definitions require the dynamic Realm exporter."
                ],
                "examples": [],
                "inflections": [],
                "etymology": "",
                "references": [],
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(json.dumps({"mode": "string_probe_fallback", "records": len(words), "tagged_text_fragments_seen": tagged_count}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
