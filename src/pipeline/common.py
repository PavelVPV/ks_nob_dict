from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT/'tmp'/'build'
DIST = ROOT/'dist'
RELEASE = ROOT/'release'
DEBUG = ROOT/'debug'
SCHEMA = DEBUG/'schema'
EXPORT_DEBUG = DEBUG/'export'
REALM = BUILD/'realm'/'ordboken.realm'
JSONL = BUILD/'ordbokene.jsonl'

def ensure_dirs():
    for p in [BUILD,DIST,RELEASE,SCHEMA,EXPORT_DEBUG]: p.mkdir(parents=True, exist_ok=True)
