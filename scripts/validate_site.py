from pathlib import Path
import json,re
root=Path(__file__).resolve().parents[1]
required=['index.html','news.html','article.html','platforms.html','destinations.html','destination.html','travel-guide.html','reports.html','about.html','editorial-policy.html','assets/site.css','assets/site.js','news.json','news-seed.json','feed.xml','scripts/update_rss.py','assets/images/iran-panorama.svg','assets/images/isfahan.svg','assets/images/rasht.svg','assets/images/yazd.svg','assets/images/shiraz.svg','assets/images/kish.svg','assets/images/desert.svg','assets/images/guesthouse.svg','assets/images/world.svg']
missing=[p for p in required if not (root/p).is_file()]
if missing:raise SystemExit('Missing files: '+', '.join(missing))
data=json.loads((root/'news.json').read_text(encoding='utf-8'));items=data.get('items',[])
if len(items)<100:raise SystemExit('News archive must contain at least 100 articles; found '+str(len(items)))
if sum(1 for x in items if x.get('region')=='iran')<80:raise SystemExit('Archive needs at least 80 Iran-focused articles')
if sum(1 for x in items if x.get('region')=='world')<5:raise SystemExit('Archive needs at least 5 global articles')
site_js=(root/'assets/site.js').read_text(encoding='utf-8')
if 'async function load()' not in site_js or "fetch('news.json?refresh=1'" not in site_js:raise SystemExit('News JSON loader is missing')
if 'await load();latest();newsPage();destination();article();citySearch();photoBacks();menu()' not in site_js:raise SystemExit('Site initialization sequence is missing')
for asset in ['assets/images/photos/iran-panorama.jpg','assets/images/photos/isfahan.jpg','assets/images/photos/rasht.jpg','assets/images/photos/yazd.jpg','assets/images/photos/shiraz.jpg','assets/images/photos/kish.jpg','assets/images/photos/qeshm.jpg','assets/images/photos/tehran.jpg','assets/images/photos/persepolis.jpg','assets/images/photos/desert.jpg','assets/images/photos/guesthouse.jpg','assets/images/platforms/jabama-cover.jpg','assets/images/platforms/mihmansho-cover.jpg','assets/images/platforms/shab-cover.jpg','assets/images/platforms/jajiga-cover.jpg','assets/images/platforms/otaghak-cover.jpg','assets/images/platforms/art-jabama.webp','assets/images/platforms/art-jajiga.webp','assets/images/platforms/art-mihmansho.webp','assets/images/platforms/art-shab.webp']:
 if not (root/asset).is_file():raise SystemExit('Missing local photo: '+asset)
for page in root.glob('*.html'):
 body=page.read_text(encoding='utf-8')
 if re.search(r'۹۰٪|۱۰٪|90%|10%',body):raise SystemExit('Internal content ratio shown publicly: '+page.name)
 if 'images.unsplash.com' in body or 'google.com/s2/favicons' in body:raise SystemExit('External image dependency found: '+page.name)
title_keys=[''.join(ch for ch in str(x.get('title','')).casefold() if ch.isalnum()) for x in items]
if len(title_keys)!=len(set(title_keys)):raise SystemExit('Duplicate news titles detected')
for x in items:
 if len(str(x.get('summary','')).strip())<60:raise SystemExit('Headline-only news summary: '+str(x.get('title','')))
ids=[x.get('id') for x in items if x.get('id')]
if len(ids)!=len(set(ids)):raise SystemExit('Duplicate news IDs')
for x in items:
 if not x.get('title') or not str(x.get('sourceUrl','')).startswith(('https://','http://')):raise SystemExit('News item missing source URL')
pages=list(root.glob('*.html'));known={p.name for p in pages};broken=[]
for p in pages:
 text=p.read_text(encoding='utf-8')
 for href in re.findall(r'href=["\']([^"\']+)',text):
  if href.startswith(('http://','https://','mailto:','tel:','#','javascript:')):continue
  target=href.split('?')[0].split('#')[0]
  if target and target not in known and not (root/target).exists():broken.append(p.name+': '+href)
if broken:raise SystemExit('Broken local links: '+', '.join(broken))
print('OK:',len(pages),'HTML pages;',len(items),'news items; links, local images and assets checked.')
