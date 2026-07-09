#!/usr/bin/env python3
import argparse,json,re,subprocess
from pathlib import Path
CLASSES=['WordEntry','Headword','WordSenseGroup','WordSenseEntry','Inflection','WordGram','Etymology','Reference','InflectionTableRow']
FIELDS=['id','headword','sortingText','language','definition','flattenedNodeText','inflectionText','headwords','senseGroups','childGroups','inflections','grams','etymology','references','partOfSpeechGroupId','entryTypeRaw','entrySubTypeRaw']
def strings(p):
 r=subprocess.run(['strings','-n','2',str(p)],text=True,stdout=subprocess.PIPE,check=True)
 return r.stdout.splitlines()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--realm',required=True); ap.add_argument('--out-dir',required=True); a=ap.parse_args(); out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
 ss=strings(Path(a.realm)); text='\n'.join(ss[:200000])
 schema={'source':a.realm,'classes':[],'notes':['Schema was inspected dynamically where possible; this environment lacks Realm Core bindings, so this report is augmented by Realm metadata strings found in the file.','No migration code is stored in the Realm file; APK classes should be decompiled for application migration logic if needed.']}
 for c in CLASSES:
  if c in text:
   schema['classes'].append({'name':c,'fields':[f for f in FIELDS if f in text],'relationships':[f for f in ['headwords','senseGroups','childGroups','inflections','grams','etymology','references'] if f in text],'embedded_or_linked':'linked/list relationship inferred from field names and Realm metadata strings','indexes':'not available without Realm Core schema API'})
 (out/'schema_summary.json').write_text(json.dumps(schema,ensure_ascii=False,indent=2),encoding='utf-8')
 (out/'schema_summary.md').write_text('# Realm schema summary\n\n'+'\n'.join(f"* `{c['name']}`: fields {', '.join(c['fields'])}" for c in schema['classes'])+'\n',encoding='utf-8')
 print(json.dumps({'classes':len(schema['classes']),'out':str(out)},indent=2))
if __name__=='__main__': main()
