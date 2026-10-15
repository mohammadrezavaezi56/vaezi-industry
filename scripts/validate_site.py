from pathlib import Path
import json,re
root=Path(__file__).resolve().parents[1]
required=['index.html','news.html','article.html','platforms.html','destinations.html','destination.html','travel-guide.html','reports.html','about.html','editorial-policy.html','assets/site.css','assets/site.js','news.json','feed.xml','scripts/update_rss.py']
missing=[p for p in required if not (root/p).is_file()]
if missing: raise SystemExit('Missing: '+', '.join(missing))
data=json.loads((root/'news.json').read_text(encoding='utf-8')); items=data.get('items',[])
ids=[x.get('id') for x in items if x.get('id')]
if len(ids)!=len(set(ids)): raise SystemExit('Duplicate news IDs')
for x in items:
 if not x.get('title') or not str(x.get('sourceUrl','')).startswith(('https://','http://')): raise SystemExit('Missing title/source URL')
pages=list(root.glob('*.html')); known={p.name for p in pages}; broken=[]
for p in pages:
 txt=p.read_text(encoding='utf-8')
 for href in re.findall(r'href=["\']([^"\']+)',txt):
  if href.startswith(('http://','https://','mailto:','tel:','#','javascript:')): continue
  t=href.split('?')[0].split('#')[0]
  if t and t not in known and not (root/t).exists(): broken.append(f'{p.name}: {href}')
if broken: raise SystemExit('Broken local links: '+', '.join(broken))
print('OK:',len(pages),'HTML pages;',len(items),'news items; all required files and local links present.')
