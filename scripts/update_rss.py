#!/usr/bin/env python3
"""Collect tourism headlines; preserve manual seeds, prefer Iran 90/10."""
import json,re,time,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
from email.utils import parsedate_to_datetime
from html import unescape
from urllib.parse import quote
from urllib.request import Request,urlopen
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parents[1]; NEWS=ROOT/'news.json'; FEED=ROOT/'feed.xml'
DIRECT=[
 ('خبرگزاری مهر','https://www.mehrnews.com/rss'),
 ('خبرگزاری ایسنا','https://www.isna.ir/rss'),
 ('خبرآنلاین','https://www.khabaronline.ir/rss'),
 ('باشگاه خبرنگاران جوان','https://www.yjc.ir/fa/rss/allnews'),
 ('تسنیم','https://www.tasnimnews.ir/fa/rss'),
]
GOOGLE_IRAN=[
 ('جست‌وجوی گردشگری ایران','گردشگری ایران OR صنعت گردشگری ایران when:30d','گردشگری ایران'),
 ('جست‌وجوی اقامتگاه','اقامتگاه بوم‌گردی OR هتل ایران گردشگری when:30d','اقامت و هتلداری'),
 ('جست‌وجوی پلتفرم اقامت','جاباما OR جاجیگا OR میهمان‌شو OR شب رزرو اقامتگاه when:30d','پلتفرم‌های اقامت'),
]
GOOGLE_WORLD=[('روند جهانی','tourism hospitality hotel travel industry when:14d','روند جهانی')]
TERMS=['گردشگری','اقامتگاه','بوم گردی','بوم‌گردی','هتل','مسافرت','سفر','جاذبه','گردشگر','توریسم','میراث فرهنگی','صنایع دستی','موزه','گردشگری سلامت','قطار گردشگری','هتل داری','پلتفرم رزرو']
HEAD={'User-Agent':'VAEZI-INDUSTRY-RSS/1.0 (+https://mohammadrezavaezi56.github.io/vaezi-industry/)'}
def clean(s):
 return re.sub(r'\\s+',' ',unescape(re.sub(r'<[^>]+>',' ',s or ''))).strip()
def dateparse(s):
 try:
  d=parsedate_to_datetime(s)
  if d.tzinfo is None:d=d.replace(tzinfo=timezone.utc)
  return d.astimezone(timezone.utc).isoformat(timespec='seconds')
 except Exception:
  try:
   d=datetime.fromisoformat(s.replace('Z','+00:00'))
   return d.astimezone(timezone.utc).isoformat(timespec='seconds')
  except Exception:return ''
def textchild(node,*names):
 for ch in node.iter():
  tag=ch.tag.split('}')[-1].lower()
  if tag in [n.lower() for n in names] and ch.text:return ch.text
 return ''
def parse_xml(payload,source,region,category,google=False):
 root=ET.fromstring(payload); rows=[]
 for node in root.iter():
  if node.tag.split('}')[-1].lower() not in ('item','entry'):continue
  title=clean(textchild(node,'title')); link=textchild(node,'link'); 
  if not link:
   for child in node:
    if child.tag.split('}')[-1].lower()=='link':
     link=child.attrib.get('href',''); 
     if link:break
  link=(link or '').strip()
  if not title or not link.startswith('http'):continue
  summary=clean(textchild(node,'description','summary','content'))
  pub=dateparse(textchild(node,'pubDate','published','updated','date'))
  srcnode=next((c for c in node if c.tag.split('}')[-1].lower()=='source'),None)
  src=clean(srcnode.text if srcnode is not None and srcnode.text else source)
  if not google and not any(t in (title+' '+summary).replace('\u200c',' ') for t in TERMS):continue
  if not pub:continue
  digest=hashlib.sha1(link.encode()).hexdigest()[:14]
  rows.append({'id':'rss-'+digest,'title':title,'summary':summary[:420] or 'برای جزئیات بیشتر، گزارش ناشر را باز کنید.','body':'این عنوان از خبرخوان RSS کشف شده است؛ خلاصهٔ کوتاه برای آشنایی اولیه است. برای جزئیات، زمینه و اصلاحیه‌ها گزارش ناشر را بررسی کنید.','source':src or source,'sourceUrl':link,'publishedAt':pub,'region':region,'category':category,'image':'world' if region=='world' else 'iran-panorama','kind':'rss'})
 return rows
def get(url):
 with urlopen(Request(url,headers=HEAD),timeout=20) as r:return ET.fromstring(r.read(2_000_000))
def google_feed(query,region,category):
 params='hl=en-US&gl=US&ceid=US:en' if region=='world' else 'hl=fa-IR&gl=IR&ceid=IR:fa'
 url='https://news.google.com/rss/search?q='+quote(query)+'&'+params
 with urlopen(Request(url,headers=HEAD),timeout=20) as r:return r.read(2_000_000)
def dedupe(rows):
 seen=set();out=[]
 for x in sorted(rows,key=lambda a:a.get('publishedAt',''),reverse=True):
  k=re.sub(r'[^\\w]+','',x.get('title','').lower())
  if k and k not in seen:seen.add(k);out.append(x)
 return out
def makefeed(items):
 now=datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT');parts=[]
 for x in items[:30]:
  try:pub=datetime.fromisoformat(x.get('publishedAt','').replace('Z','+00:00')).strftime('%a, %d %b %Y %H:%M:%S GMT')
  except Exception:pub=now
  parts.append('<item><title>'+escape(x.get('title',''))+'</title><link>'+escape(x.get('sourceUrl',''))+'</link><guid isPermaLink="false">'+escape(x.get('id',''))+'</guid><pubDate>'+escape(pub)+'</pubDate><description>'+escape(x.get('summary','')[:500])+'</description></item>')
 return '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>VAEZI INDUSTRY | گردشگری ایران</title><link>https://mohammadrezavaezi56.github.io/vaezi-industry/</link><description>خبرهای منبع‌دار گردشگری ایران و گزیده‌ای از جهان</description><language>fa</language><lastBuildDate>'+now+'</lastBuildDate>'+''.join(parts)+'</channel></rss>\n'
def main():
 old=json.loads(NEWS.read_text(encoding='utf-8')) if NEWS.exists() else {'items':[]}
 prev=old if isinstance(old,list) else old.get('items',[])
 # Keep every manually curated item; never discard them when one provider returns an empty feed.
 manual=[x for x in prev if x.get('manual') or x.get('kind')!='rss']
 prior=[x for x in prev if x.get('kind')=='rss']
 fi=[];fw=[];fail=[];success=0
 for name,url in DIRECT:
  try:
   with urlopen(Request(url,headers=HEAD),timeout=20) as r:payload=r.read(2_000_000)
   rows=parse_xml(payload,name,'iran','اخبار گردشگری',False);fi.extend(rows);success+=1;print('OK source',name,'tourism items',len(rows))
  except Exception as e:fail.append(name+': '+str(e));print('WARN source',name,str(e))
  time.sleep(.2)
 for name,q,cat in GOOGLE_IRAN:
  try:fi.extend(parse_xml(google_feed(q,'iran',cat),name,'iran',cat,True));success+=1;print('OK Google Iran',name)
  except Exception as e:fail.append(name+': '+str(e));print('WARN Google Iran',name,str(e))
 for name,q,cat in GOOGLE_WORLD:
  try:fw.extend(parse_xml(google_feed(q,'world',cat),name,'world',cat,True));success+=1;print('OK Google World',name)
  except Exception as e:fail.append(name+': '+str(e));print('WARN Google World',name,str(e))
 iran=dedupe([x for x in manual if x.get('region')!='world']+[x for x in prior if x.get('region')!='world']+fi)
 world=dedupe([x for x in manual if x.get('region')=='world']+[x for x in prior if x.get('region')=='world']+fw)
 if success==0:
  if not manual and not prior:raise SystemExit('All feeds failed and there is no fallback content.')
  print('All providers failed; retaining existing published items.')
  items=dedupe(manual+prior)
 else:
  # Target 90/10 at up to 30 cards; preserve a usable Iran-first list even if feeds are empty.
  items=iran[:27]+world[:3]
  if not items:items=dedupe(manual+prior)
  items.sort(key=lambda x:x.get('publishedAt',''),reverse=True)
 payload={'updatedAt':datetime.now(timezone.utc).isoformat(timespec='seconds'),'mix':{'iranTargetPercent':90,'worldTargetPercent':10},'feedStatus':{'configuredFeeds':len(DIRECT)+len(GOOGLE_IRAN)+len(GOOGLE_WORLD),'successfulFeeds':success,'warnings':fail},'items':items}
 NEWS.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 FEED.write_text(makefeed(items),encoding='utf-8')
 print('Wrote',len(items),'items;',sum(x.get('region')!='world' for x in items),'Iran-focused,',sum(x.get('region')=='world' for x in items),'world.')
if __name__=='__main__':main()
