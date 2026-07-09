#!/usr/bin/env python3
import argparse,json,re,subprocess,html
from pathlib import Path
WORD_RE=re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿÆØÅæøå0-9][A-Za-zÀ-ÖØ-öø-ÿÆØÅæøå0-9 .,'’()\-/]{1,58}$")
TAG_RE=re.compile(r"\|[A-Za-z]+z?|\|[KQ]\d+(?:nn|nb)?|\|[a-z]{2}")
BAD={'AAAA','metadata','class','version','id','true','false'}
def iter_strings(p):
 r=subprocess.run(['strings','-n','2',str(p)],text=True,stdout=subprocess.PIPE,check=True)
 yield from (x.strip('\x00').strip() for x in r.stdout.splitlines())
def clean(s): return re.sub(r'\s+',' ',TAG_RE.sub(' ',s).replace('AAAA',' ')).strip(' |;,')
def is_word(s):
 return bool(s and s not in BAD and '|' not in s and 'AAAA' not in s and 2<=len(s)<=58 and WORD_RE.match(s) and sum(ch.isalpha() for ch in s)>=2)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--realm',required=True); ap.add_argument('--out',required=True); ap.add_argument('--sample',type=int,default=0); a=ap.parse_args(); out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
 seen=set(); records=0; tagged=0
 with out.open('w',encoding='utf-8') as f:
  for s in iter_strings(Path(a.realm)):
   if '|' in s and len(s)>12:
    tagged+=1; continue
   if not is_word(s): continue
   key=s.casefold()
   if key in seen: continue
   seen.add(key); records+=1
   rec={'id':f'ordbokene-{records}','language':'nb/nn','headword':s,'part_of_speech':'','definitions':['Entry extracted from the offline Ordbøkene Realm database. Install as a personal Kindle lookup index; richer definitions require Realm Core bindings for full object graph traversal.'],'examples':[],'inflections':[],'etymology':'','references':[]}
   f.write(json.dumps(rec,ensure_ascii=False)+'\n')
   if a.sample and records>=a.sample: break
 print(json.dumps({'records':records,'tagged_fragments_seen':tagged,'out':str(out)},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
