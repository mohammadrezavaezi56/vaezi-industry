#!/usr/bin/env python3
"""Collect tourism headlines, preserving curated fallback content and source links."""
import json,time,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
from email.utils import parsedate_to_datetime
from html import unescape
from urllib.parse import quote
from urllib.request import Request,urlopen
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parents[1]
NEWS=ROOT/'news.json'; SEEDS=ROOT/'news-seed.json'; FEED=ROOT/'feed.xml'
DIRECT=[
 ('خبرگزاری مهر','https://www.mehrnews.com/rss'),
 ('خبرگزاری ایسنا','https://www.isna.ir/rss'),
 ('خبرآنلاین','https://www.khabaronline.ir/rss'),
 ('باشگاه خبرنگاران جوان','https://www.yjc.ir/fa/rss/allnews'),
]
QUERIES_IR=[
 ('گردشگری ایران','گردشگری ایران OR صنعت گردشگری ایران when:30d','گردشگری ایران'),
 ('اقامتگاه و هتل','اقامتگاه بوم گردی OR هتل ایران گردشگری when:30d','اقامت و هتلداری'),
 ('پلتفرم اقامت','جاباما OR جاجیگا OR میهمان شو OR شب رزرو اقامتگاه when:30d','پلتفرم‌های اقامت'),
]
QUERIES_WORLD=[('گردشگری جهان','tourism hospitality hotel travel industry when:14d','روند جهانی')]
TERMS=['گردشگری','اقامتگاه','بوم گردی','بوم‌گردی','هتل','مسافرت','سفر','جاذبه','گردشگر','توریسم','میراث فرهنگی','صنایع دستی','موزه','قطار گردشگری','پلتفرم رزرو']
HEAD={'User-Agent':'VAEZI-INDUSTRY-RSS/1.0'}
def clean(value):
 return ' '.join(unescape(' '.join((value or '').split())).replace('<',' ').replace('>',' ').split())
def dateparse(value):
 for parser in (parsedate_to_datetime,datetime.fromisoformat):
  try:
   d=parser(value.replace('Z','+00:00')) if parser is datetime.fromisoformat else parser(value)
   if d.tzinfo is None:d=d.replace(tzinfo=timezone.utc)
   return d.astimezone(timezone.utc).isoformat(timespec='seconds')
  except Exception:pass
 return ''
def node_text(node,names):
 for child in node.iter():
  if child.tag.split('}')[-1].lower() in names and child.text:return child.text
 return ''
def parse_feed(payload,source,region,category,google=False):
 root=ET.fromstring(payload);out=[]
 for node in root.iter():
  if node.tag.split('}')[-1].lower() not in ('item','entry'):continue
  title=clean(node_text(node,{'title'}));link=node_text(node,{'link'})
  if not link:
   for child in node:
    if child.tag.split('}')[-1].lower()=='link' and child.attrib.get('href'):
     link=child.attrib['href'];break
  link=(link or '').strip()
  if not title or not link.startswith(('http://','https://')):continue
  summary=clean(node_text(node,{'description','summary','content'}))
  if not google and not any(word in (title+' '+summary).replace('‌',' ') for word in TERMS):continue
  published=dateparse(node_text(node,{'pubdate','published','updated','date'}))
  if not published:continue
  src=''; 
  for child in node:
   if child.tag.split('}')[-1].lower()=='source' and child.text:src=clean(child.text);break
  digest=hashlib.sha1(link.encode()).hexdigest()[:14]
  out.append({'id':'rss-'+digest,'title':title,'summary':summary[:420] or 'برای جزئیات بیشتر، گزارش ناشر را باز کنید.','body':'این عنوان از خبرخوان RSS کشف شده است؛ خلاصه برای آشنایی اولیه است. برای جزئیات، زمینه و اصلاحیه‌ها گزارش ناشر را بررسی کنید.','source':src or source,'sourceUrl':link,'publishedAt':published,'region':region,'category':category,'image':'world' if region=='world' else 'iran-panorama','kind':'rss'})
 return out
def get_payload(url):
 with urlopen(Request(url,headers=HEAD),timeout=18) as response:return response.read(2_000_000)
def google_feed(query,region):
 params='hl=en-US&gl=US&ceid=US:en' if region=='world' else 'hl=fa-IR&gl=IR&ceid=IR:fa'
 return get_payload('https://news.google.com/rss/search?q='+quote(query)+'&'+params)
def dedupe(rows):
 seen=set();out=[]
 for item in sorted(rows,key=lambda x:x.get('publishedAt',''),reverse=True):
  key=''.join(ch for ch in item.get('title','').casefold() if ch.isalnum())
  if key and key not in seen:seen.add(key);out.append(item)
 return out
def make_feed(items):
 now=datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT');parts=[]
 for item in items[:30]:
  try:published=datetime.fromisoformat(item.get('publishedAt','').replace('Z','+00:00')).strftime('%a, %d %b %Y %H:%M:%S GMT')
  except Exception:published=now
  parts.append('<item><title>'+escape(item.get('title',''))+'</title><link>'+escape(item.get('sourceUrl',''))+'</link><guid isPermaLink="false">'+escape(item.get('id',''))+'</guid><pubDate>'+escape(published)+'</pubDate><description>'+escape(item.get('summary','')[:500])+'</description></item>')
 return '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>VAEZI INDUSTRY | گردشگری ایران</title><link>https://mohammadrezavaezi56.github.io/vaezi-industry/</link><description>خبرهای گردشگری ایران و گزیده‌ای از جهان</description><language>fa</language><lastBuildDate>'+now+'</lastBuildDate>'+''.join(parts)+'</channel></rss>\n'
def main():
 seed_data=json.loads(SEEDS.read_text(encoding='utf-8'));seed_items=seed_data.get('items',[])
 previous=json.loads(NEWS.read_text(encoding='utf-8')) if NEWS.exists() else {'items':[]}
 prev=previous if isinstance(previous,list) else previous.get('items',[])
 previous_rss=[x for x in prev if x.get('kind')=='rss']
 iran_new=[];world_new=[];warnings=[];succeeded=0
 for name,url in DIRECT:
  try:
   rows=parse_feed(get_payload(url),name,'iran','اخبار گردشگری')
   iran_new.extend(rows);succeeded+=1;print('OK direct source:',name,'items:',len(rows))
  except Exception as error:warnings.append(name+': '+str(error));print('WARN direct source:',name,error)
  time.sleep(.2)
 for name,query,category in QUERIES_IR:
  try:
   rows=parse_feed(google_feed(query,'iran'),'Google News RSS · '+name,'iran',category,True)
   iran_new.extend(rows);succeeded+=1;print('OK search:',name,'items:',len(rows))
  except Exception as error:warnings.append(name+': '+str(error));print('WARN search:',name,error)
 for name,query,category in QUERIES_WORLD:
  try:
   rows=parse_feed(google_feed(query,'world'),'Google News RSS · '+name,'world',category,True)
   world_new.extend(rows);succeeded+=1;print('OK world:',name,'items:',len(rows))
  except Exception as error:warnings.append(name+': '+str(error));print('WARN world:',name,error)
 seed_iran=[x for x in seed_items if x.get('region')!='world']
 seed_world=[x for x in seed_items if x.get('region')=='world']
 iran=dedupe(seed_iran+[x for x in previous_rss if x.get('region')!='world']+iran_new)
 world=dedupe(seed_world+[x for x in previous_rss if x.get('region')=='world']+world_new)
 if succeeded==0 and not previous_rss:
  print('All feeds failed; only curated seed stories will remain.')
 items=iran[:27]+world[:3]
 if not items:items=seed_items
 items.sort(key=lambda x:x.get('publishedAt',''),reverse=True)
 payload={'updatedAt':datetime.now(timezone.utc).isoformat(timespec='seconds'),'mix':{'iranTargetPercent':90,'worldTargetPercent':10},'feedStatus':{'configuredFeeds':len(DIRECT)+len(QUERIES_IR)+len(QUERIES_WORLD),'successfulFeeds':succeeded,'warnings':warnings},'items':items}
 NEWS.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 FEED.write_text(make_feed(items),encoding='utf-8')
 print('Published',len(items),'stories; Iran:',sum(x.get('region')!='world' for x in items),'World:',sum(x.get('region')=='world' for x in items))
if __name__=='__main__':main()
