#!/usr/bin/env python3
"""Update source-linked tourism headlines: Iran first, max 10% international."""
import json,re,time,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
from email.utils import parsedate_to_datetime
from html import unescape
from urllib.parse import quote
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]; NEWS=ROOT/'news.json'; FEED=ROOT/'feed.xml'
IRAN=[
 ('بازآفرینی و سیاست گردشگری','سند بازآفرینی گردشگری ایران OR گردشگری ایران سیاست گذاری when:30d','سیاست‌گذاری'),
 ('اقتصاد گردشگری ایران','تسهیلات گردشگری ایران OR سرمایه گذاری گردشگری ایران when:30d','سرمایه‌گذاری'),
 ('هتل و اقامتگاه ایران','هتل ایران OR اقامتگاه بوم گردی ایران when:30d','اقامت و هتلداری'),
 ('مقصدهای ایران','جاذبه گردشگری ایران OR گردشگری استان ها when:30d','مقصدهای ایران'),
 ('پلتفرم های رزرو','جاباما OR جاجیگا OR میهمان شو OR شب اقامتگاه when:30d','پلتفرم‌های اقامت')
]
WORLD=[('گردشگری جهان','tourism hospitality hotel industry travel when:14d','روند جهانی')]
HEAD={'User-Agent':'VAEZI-INDUSTRY-RSS/1.0'}
def clean(s):
 return re.sub(r'\\s+',' ',unescape(re.sub(r'<[^>]+>',' ',s or ''))).strip()
def dt(s):
 try:
  x=parsedate_to_datetime(s)
  return x.astimezone(timezone.utc).isoformat(timespec='seconds')
 except Exception:return ''
def fetch(name,q,region,category):
 lang='en-US&gl=US&ceid=US:en' if region=='world' else 'fa-IR&gl=IR&ceid=IR:fa'
 url='https://news.google.com/rss/search?q='+quote(q)+'&hl='+lang
 with urlopen(Request(url,headers=HEAD),timeout=20) as r: root=ET.fromstring(r.read(2_000_000))
 out=[]
 for it in root.findall('./channel/item'):
  title=clean(it.findtext('title','')); link=(it.findtext('link','') or '').strip()
  if not title or not link.startswith('http'):continue
  pub=dt(it.findtext('pubDate','')); sn=it.find('source'); source=clean(sn.text if sn is not None else 'ناشر خبر')
  digest=hashlib.sha1((link or title).encode()).hexdigest()[:14]
  out.append({'id':'rss-'+digest,'title':title,'summary':'خلاصهٔ فید برای آشنایی اولیه است؛ برای متن، جزئیات و اصلاحیه‌ها گزارش ناشر را باز کنید.','body':'این عنوان از خبرخوان RSS کشف شده است. محتوای کامل در وب‌سایت ناشر قرار دارد؛ پیش از نقل جزئیات، منبع و تاریخ را بررسی کنید.','source':source,'sourceUrl':link,'publishedAt':pub,'region':region,'category':category,'image':'world' if region=='world' else 'iran-panorama','kind':'rss'})
 return out
def dedupe(items):
 seen=set(); out=[]
 for x in sorted(items,key=lambda a:a.get('publishedAt',''),reverse=True):
  k=re.sub(r'[^\\w]+','',x.get('title','').lower())
  if k and k not in seen:seen.add(k);out.append(x)
 return out
def makefeed(items):
 from xml.sax.saxutils import escape
 now=datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
 rows=[]
 for x in items[:30]:
  d=x.get('publishedAt','')
  try:d=datetime.fromisoformat(d.replace('Z','+00:00')).strftime('%a, %d %b %Y %H:%M:%S GMT')
  except Exception:d=now
  rows.append('<item><title>'+escape(x.get('title',''))+'</title><link>'+escape(x.get('sourceUrl',''))+'</link><guid isPermaLink="false">'+escape(x.get('id',''))+'</guid><pubDate>'+escape(d)+'</pubDate><description>'+escape(x.get('summary','')[:500])+'</description></item>')
 return '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>VAEZI INDUSTRY | گردشگری ایران</title><link>https://mohammadrezavaezi56.github.io/vaezi-industry/</link><description>خبرهای منبع‌دار گردشگری ایران و گزیده‌ای از جهان</description><language>fa</language><lastBuildDate>'+now+'</lastBuildDate>'+''.join(rows)+'</channel></rss>'
def main():
 old=json.loads(NEWS.read_text(encoding='utf-8')) if NEWS.exists() else {'items':[]}
 olditems=old if isinstance(old,list) else old.get('items',[])
 manual=[x for x in olditems if x.get('manual') or x.get('kind')=='manual']
 oldrss=[x for x in olditems if x.get('kind')=='rss']
 iran=[];world=[];failed=[]
 for n,q,c in IRAN:
  try:iran += fetch(n,q,'iran',c);print('OK:',n)
  except Exception as e:failed.append(n+': '+str(e));print('WARN:',n,e)
  time.sleep(.2)
 for n,q,c in WORLD:
  try:world += fetch(n,q,'world',c);print('OK:',n)
  except Exception as e:failed.append(n+': '+str(e));print('WARN:',n,e)
 iran=dedupe(manual+[x for x in oldrss if x.get('region')!='world']+iran)
 world=dedupe([x for x in oldrss if x.get('region')=='world']+world)
 if not iran and not world:raise SystemExit('No feeds succeeded; keeping current published file unchanged.')
 # 90/10 target at 30 items; reserve at least the known manual seed stories.
 items=iran[:27]+world[:3]
 items.sort(key=lambda x:x.get('publishedAt',''),reverse=True)
 payload={'updatedAt':datetime.now(timezone.utc).isoformat(timespec='seconds'),'mix':{'iranTargetPercent':90,'worldTargetPercent':10},'feedStatus':{'configuredFeeds':len(IRAN)+len(WORLD),'successfulFeeds':len(IRAN)+len(WORLD)-len(failed),'warnings':failed},'items':items}
 NEWS.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 FEED.write_text(makefeed(items),encoding='utf-8')
 print('Published',len(items),'items:',sum(x.get('region')!='world' for x in items),'Iran-focused and',sum(x.get('region')=='world' for x in items),'world.')
if __name__=='__main__':main()
