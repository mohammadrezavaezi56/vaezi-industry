#!/usr/bin/env python3
"""Source-linked tourism RSS collector. Curated fallback stories are never discarded."""
import json,time,hashlib,re,xml.etree.ElementTree as ET
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
IR_QUERIES=[
 ('گردشگری ایران','گردشگری ایران OR صنعت گردشگری ایران when:30d','گردشگری ایران'),
 ('اقامتگاه و هتل','اقامتگاه بوم گردی OR هتل ایران گردشگری when:30d','اقامت و هتلداری'),
 ('پلتفرم اقامت','جاباما OR جاجیگا OR میهمان شو OR شب رزرو اقامتگاه when:30d','پلتفرم‌های اقامت'),
]
WORLD_QUERIES=[('روند جهانی','tourism hospitality hotel travel industry when:14d','روند جهانی')]
IR_TERMS=['گردشگری','گردشگر','توریسم','هتل','اقامتگاه','بوم گردی','بوم‌گردی','سفر','مسافرت','میراث فرهنگی','میراث‌فرهنگی','موزه','جاذبه','صنایع دستی','صنایع‌دستی','هتلداری','هتل‌داری','اکوتوریسم','طبیعت گردی','طبیعت‌گردی','روستا','گردشگری دریایی','گردشگری ساحلی','گردشگری شهری','نمایشگاه گردشگری','هتلدار','گردشگرپذیر','توریستی']
EN_TERMS=['tourism','tourist','hotel','resort','airline','cruise','destination','visitor economy','accommodation','travel demand','tourism industry','travel industry','hotel occupancy','hotel market','hospitality industry','hospitality market']
BAD_TERMS=['پاراوزنه','ملی پوش','ملی‌پوش','واحد مسکونی','هوش مصنوعی عکس','عکس دهه شصتی','فوتبال','والیبال','بسکتبال','بورس','قیمت دلار','تیم ملی','آبرسانی']
HEAD={'User-Agent':'VAEZI-INDUSTRY-RSS/1.1'}
def clean(value):
 return ' '.join(unescape(re.sub(r'<[^>]+>',' ',value or '')).split())
def parse_date(value):
 for mode in (0,1):
  try:
   d=parsedate_to_datetime(value) if mode==0 else datetime.fromisoformat(value.replace('Z','+00:00'))
   if d.tzinfo is None:d=d.replace(tzinfo=timezone.utc)
   return d.astimezone(timezone.utc).isoformat(timespec='seconds')
  except Exception:pass
 return ''
def text_child(node,names):
 for child in node.iter():
  if child.tag.split('}')[-1].lower() in names and child.text:return child.text
 return ''
def relevant(title,region):
 t=title.casefold().replace('‌',' ')
 if any(bad in t for bad in BAD_TERMS):return False
 terms=EN_TERMS if region=='world' else IR_TERMS
 return any(term in t for term in terms)
def parse_feed(payload,source,region,category,google=False):
 root=ET.fromstring(payload);items=[]
 for node in root.iter():
  if node.tag.split('}')[-1].lower() not in ('item','entry'):continue
  title=clean(text_child(node,{'title'}));link=text_child(node,{'link'})
  if not link:
   for child in node:
    if child.tag.split('}')[-1].lower()=='link' and child.attrib.get('href'):
     link=child.attrib['href'];break
  link=(link or '').strip()
  if not title or not link.startswith(('http://','https://')) or not relevant(title,region):continue
  summary=clean(text_child(node,{'description','summary','content'}))
  published=parse_date(text_child(node,{'pubdate','published','updated','date'}))
  if not published:continue
  src=''
  for child in node:
   if child.tag.split('}')[-1].lower()=='source' and child.text:src=clean(child.text);break
  if not src or src.casefold() in ('بدون منبع','unknown'):src=source
  digest=hashlib.sha1(link.encode()).hexdigest()[:14]
  items.append({'id':'rss-'+digest,'title':title,'summary':summary[:420] or 'برای جزئیات بیشتر، گزارش ناشر را باز کنید.','body':'این عنوان از خبرخوان RSS کشف شده است؛ خلاصه برای آشنایی اولیه است. برای جزئیات، زمینه و اصلاحیه‌ها گزارش ناشر را بررسی کنید.','source':src,'sourceUrl':link,'publishedAt':published,'region':region,'category':category,'image':'world' if region=='world' else 'iran-panorama','kind':'rss'})
 return items
def fetch(url):
 with urlopen(Request(url,headers=HEAD),timeout=18) as response:return response.read(2_000_000)
def google(query,region):
 params='hl=en-US&gl=US&ceid=US:en' if region=='world' else 'hl=fa-IR&gl=IR&ceid=IR:fa'
 return fetch('https://news.google.com/rss/search?q='+quote(query)+'&'+params)
def dedupe(rows):
 seen=set();result=[]
 for item in sorted(rows,key=lambda x:x.get('publishedAt',''),reverse=True):
  key=''.join(ch for ch in item.get('title','').casefold() if ch.isalnum())
  if key and key not in seen:seen.add(key);result.append(item)
 return result
def make_feed(items):
 now=datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT');entries=[]
 for item in items[:30]:
  try:pub=datetime.fromisoformat(item.get('publishedAt','').replace('Z','+00:00')).strftime('%a, %d %b %Y %H:%M:%S GMT')
  except Exception:pub=now
  entries.append('<item><title>'+escape(item.get('title',''))+'</title><link>'+escape(item.get('sourceUrl',''))+'</link><guid isPermaLink="false">'+escape(item.get('id',''))+'</guid><pubDate>'+escape(pub)+'</pubDate><description>'+escape(item.get('summary','')[:500])+'</description></item>')
 return '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>VAEZI INDUSTRY | گردشگری ایران</title><link>https://mohammadrezavaezi56.github.io/vaezi-industry/</link><description>خبرهای گردشگری ایران و گزیده‌ای از جهان</description><language>fa</language><lastBuildDate>'+now+'</lastBuildDate>'+''.join(entries)+'</channel></rss>\n'
def main():
 seeds=json.loads(SEEDS.read_text(encoding='utf-8')).get('items',[])
 old=json.loads(NEWS.read_text(encoding='utf-8')) if NEWS.exists() else {'items':[]}
 old_items=old if isinstance(old,list) else old.get('items',[])
 previous=[x for x in old_items if x.get('kind')=='rss' and relevant(x.get('title',''),x.get('region','iran'))]
 fresh_ir=[];fresh_world=[];warnings=[];success=0
 for name,url in DIRECT:
  try:
   rows=parse_feed(fetch(url),name,'iran','اخبار گردشگری')
   fresh_ir.extend(rows);success+=1;print('OK direct',name,'accepted',len(rows))
  except Exception as error:warnings.append(name+': '+str(error));print('WARN direct',name,error)
  time.sleep(.15)
 for name,query,category in IR_QUERIES:
  try:
   rows=parse_feed(google(query,'iran'),'Google News · '+name,'iran',category,True)
   fresh_ir.extend(rows);success+=1;print('OK search',name,'accepted',len(rows))
  except Exception as error:warnings.append(name+': '+str(error));print('WARN search',name,error)
 for name,query,category in WORLD_QUERIES:
  try:
   rows=parse_feed(google(query,'world'),'Google News · '+name,'world',category,True)
   fresh_world.extend(rows);success+=1;print('OK world',name,'accepted',len(rows))
  except Exception as error:warnings.append(name+': '+str(error));print('WARN world',name,error)
 curated_ir=[x for x in seeds if x.get('region')!='world'];curated_world=[x for x in seeds if x.get('region')=='world']
 iran=dedupe(curated_ir+[x for x in previous if x.get('region')!='world']+fresh_ir)
 world=dedupe(curated_world+[x for x in previous if x.get('region')=='world']+fresh_world)
 # Keep the worldwide share close to 10%, with at least one world item when available.
 world_limit=min(3,max(1,round(len(iran)/9))) if world else 0
 items=iran[:27]+world[:world_limit]
 if not items:items=seeds
 items.sort(key=lambda x:x.get('publishedAt',''),reverse=True)
 payload={'updatedAt':datetime.now(timezone.utc).isoformat(timespec='seconds'),'mix':{'iranTargetPercent':90,'worldTargetPercent':10},'feedStatus':{'configuredFeeds':len(DIRECT)+len(IR_QUERIES)+len(WORLD_QUERIES),'successfulFeeds':success,'warnings':warnings},'items':items}
 NEWS.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 FEED.write_text(make_feed(items),encoding='utf-8')
 print('Published',len(items),'items; Iran',sum(x.get('region')!='world' for x in items),'World',sum(x.get('region')=='world' for x in items))
if __name__=='__main__':main()
