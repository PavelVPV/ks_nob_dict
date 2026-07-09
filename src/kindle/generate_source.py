#!/usr/bin/env python3
import argparse,json,html,uuid,zipfile,datetime
from pathlib import Path
def safe_id(i): return 'e'+''.join(c if c.isalnum() else '_' for c in i)[:80]
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--jsonl',required=True); ap.add_argument('--out-dir',required=True); a=ap.parse_args(); out=Path(a.out_dir); (out/'OEBPS').mkdir(parents=True,exist_ok=True); (out/'META-INF').mkdir(exist_ok=True)
 entries=[]
 for line in Path(a.jsonl).read_text(encoding='utf-8').splitlines(): entries.append(json.loads(line))
 body=[]; nav=[]
 for r in entries:
  eid=safe_id(r['id']); hw=html.escape(r['headword']); defs=''.join(f'<li>{html.escape(str(d))}</li>' for d in r.get('definitions',[]))
  infl=' '.join(html.escape(x) for x in r.get('inflections',[]))
  body.append(f'<idx:entry name="default" scriptable="yes" spell="yes"><idx:orth value="{hw}">{hw}</idx:orth><a id="{eid}"></a><h2>{hw}</h2><ol>{defs}</ol><p class="infl">{infl}</p></idx:entry>')
  nav.append(f'<li><a href="entries.xhtml#{eid}">{hw}</a></li>')
 xhtml='<?xml version="1.0" encoding="utf-8"?><!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:idx="http://www.mobipocket.com/idx"><head><title>Ordbøkene Kindle Dictionary</title><style>body{font-family:serif} h2{margin-top:1em}.infl{color:#555}</style></head><body>'+''.join(body)+'</body></html>'
 (out/'OEBPS'/'entries.xhtml').write_text(xhtml,encoding='utf-8')
 (out/'META-INF'/'container.xml').write_text('<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>',encoding='utf-8')
 opf=f'''<?xml version="1.0" encoding="utf-8"?><package xmlns="http://www.idpf.org/2007/opf" unique-identifier="uid" version="2.0"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:x-metadata="http://www.idpf.org/2007/opf"><dc:title>Ordbøkene Personal Kindle Dictionary</dc:title><dc:language>no</dc:language><dc:identifier id="uid">urn:uuid:{uuid.uuid4()}</dc:identifier><x-metadata><DictionaryInLanguage>no</DictionaryInLanguage><DictionaryOutLanguage>no</DictionaryOutLanguage></x-metadata></metadata><manifest><item id="entries" href="entries.xhtml" media-type="application/xhtml+xml"/></manifest><spine><itemref idref="entries"/></spine></package>'''
 (out/'OEBPS'/'content.opf').write_text(opf,encoding='utf-8')
 print(json.dumps({'entries':len(entries),'source':str(out)},indent=2))
if __name__=='__main__': main()
