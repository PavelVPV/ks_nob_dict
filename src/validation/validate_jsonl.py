#!/usr/bin/env python3
import argparse,json,collections
from pathlib import Path
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--jsonl',required=True); ap.add_argument('--report',required=True); a=ap.parse_args(); ids=set(); heads=collections.Counter(); bad=[]; missing=0; total=0
 for n,line in enumerate(Path(a.jsonl).read_text(encoding='utf-8').splitlines(),1):
  try: r=json.loads(line); total+=1
  except Exception as e: bad.append({'line':n,'error':str(e)}); continue
  if r.get('id') in ids: bad.append({'line':n,'error':'duplicate id'}); ids.add(r.get('id'))
  hw=r.get('headword',''); heads[hw.casefold()]+=1
  if not r.get('definitions'): missing+=1
 report={'records':total,'duplicate_headwords':sum(1 for k,v in heads.items() if v>1),'missing_definitions':missing,'malformed':bad[:20],'status':'pass' if not bad and missing==0 else 'warning'}
 Path(a.report).parent.mkdir(parents=True,exist_ok=True); Path(a.report).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
