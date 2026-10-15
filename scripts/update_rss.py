#!/usr/bin/env python3
"""Build a source-linked, tourism-focused archive from news feeds and Google News RSS."""
import concurrent.futures, hashlib, json, re, time, xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
NEWS = ROOT / "news.json"
SEEDS = ROOT / "news-seed.json"
FEED = ROOT / "feed.xml"
DIRECT = [
    ("خبرگزاری مهر", "https://www.mehrnews.com/rss"),
    ("خبرگزاری ایسنا", "https://www.isna.ir/rss"),
    ("خبرآنلاین", "https://www.khabaronline.ir/rss"),
    ("باشگاه خبرنگاران جوان", "https://www.yjc.ir/fa/rss/allnews"),
]
IR_QUERIES = [
    ("بازار گردشگری ایران", "گردشگری ایران when:365d", "بازار گردشگری"),
    ("سیاست‌گذاری گردشگری", "وزارت میراث فرهنگی گردشگری ایران when:365d", "سیاست‌گذاری"),
    ("صنعت گردشگری", "صنعت گردشگری ایران سرمایه گذاری when:365d", "سرمایه‌گذاری"),
    ("هتل و اقامت", "هتلداری ایران اقامتگاه when:365d", "اقامت و هتلداری"),
    ("اقامتگاه بوم‌گردی", "اقامتگاه بوم گردی ایران when:365d", "اقامت و هتلداری"),
    ("پلتفرم‌های اقامت", "جاباما OR جاجیگا OR میهمان شو OR اتاقک رزرو اقامتگاه when:365d", "پلتفرم‌های اقامت"),
    ("گردشگری سلامت", "گردشگری سلامت ایران when:365d", "گردشگری سلامت"),
    ("میراث فرهنگی و گردشگری", "میراث فرهنگی گردشگری ایران when:365d", "میراث فرهنگی"),
    ("ثبت جهانی آثار ایران", "یونسکو ثبت جهانی آثار ایران میراث فرهنگی when:365d", "میراث فرهنگی"),
    ("سرمایه‌گذاری گردشگری", "سرمایه گذاری گردشگری ایران پروژه هتل when:365d", "سرمایه‌گذاری"),
    ("تسهیلات گردشگری", "تسهیلات گردشگری صنایع دستی ایران when:365d", "سرمایه‌گذاری"),
    ("گردشگری روستایی", "گردشگری روستایی ایران بوم گردی when:365d", "مقصدهای ایران"),
    ("طبیعت‌گردی و اکوتوریسم", "اکوتوریسم طبیعت گردی ایران گردشگری when:365d", "گردشگری پایدار"),
    ("گردشگری ساحلی", "گردشگری ساحلی دریایی ایران when:365d", "مقصدهای ایران"),
    ("گردشگری ریلی", "قطار گردشگری ایران سفر ریلی when:365d", "حمل‌ونقل"),
    ("پرواز و سفر هوایی", "پروازهای گردشگری ایران مسیر پروازی سفر when:365d", "حمل‌ونقل"),
    ("جاذبه‌های گردشگری", "جاذبه گردشگری ایران معرفی مقصد when:365d", "مقصدهای ایران"),
    ("موزه‌ها و گردشگری فرهنگی", "موزه ایران میراث گردشگری when:365d", "میراث فرهنگی"),
    ("آمار اقامتگاه‌ها", "ضریب اشغال مراکز اقامتی هتل ایران گردشگری when:365d", "بازار اقامت"),
    ("فناوری سفر", "فناوری سفر رزرو آنلاین گردشگری ایران when:365d", "فناوری سفر"),
    ("گردشگری پایدار", "گردشگری پایدار ایران جوامع محلی when:365d", "گردشگری پایدار"),
    ("نمایشگاه و رویدادهای گردشگری", "نمایشگاه همایش رویداد گردشگری ایران when:365d", "رویدادها"),
    ("گردشگری گیلان و مازندران", "گردشگری گیلان مازندران جاذبه اقامتگاه when:365d", "مقصدهای ایران"),
    ("گردشگری فارس و شیراز", "گردشگری فارس شیراز تخت جمشید when:365d", "مقصدهای ایران"),
    ("گردشگری اصفهان و یزد", "گردشگری اصفهان یزد میراث اقامت when:365d", "مقصدهای ایران"),
    ("گردشگری خراسان و شمال شرق", "گردشگری خراسان رضوی مشهد میراث اقامت when:365d", "مقصدهای ایران"),
    ("گردشگری تهران و آذربایجان", "گردشگری تهران تبریز میراث فرهنگی when:365d", "مقصدهای ایران"),
    ("گردشگری جنوب", "گردشگری کیش قشم هرمزگان جنوب ایران when:365d", "مقصدهای ایران"),
    ("گردشگری غرب و مرکز", "گردشگری کردستان کرمانشاه همدان لرستان ایران when:365d", "مقصدهای ایران"),
    ("گردشگری تاریخی ایران", "گردشگری تاریخی کاروانسرا آثار تاریخی ایران when:365d", "میراث فرهنگی"),
    ("اقتصاد اقامت", "اقتصاد اقامت هتلداران بازار اجاره کوتاه مدت ایران when:365d", "بازار اقامت"),
    ("سفرهای داخلی", "سفرهای داخلی ایران گردشگری مقصد when:365d", "مقصدهای ایران"),
    ("آموزش گردشگری", "آزمون جامع گردشگری آموزش راهنمایان ایران when:365d", "آموزش گردشگری"),
    ("گردشگری کشاورزی و خوراک", "گردشگری کشاورزی خوراک محلی ایران روستا when:365d", "مقصدهای ایران"),
    ("گردشگری ایران به زبان انگلیسی", "Iran tourism hotels travel industry heritage when:365d", "بازارهای بین‌المللی"),
]
WORLD_QUERIES = [
    ("روندهای گردشگری جهانی", "global tourism industry travel trends when:180d", "روند جهانی"),
    ("بازار هتل‌های جهان", "hotel market hotel occupancy hotel investment 2026 when:180d", "بازار جهانی"),
    ("گردشگری خاورمیانه", "Middle East tourism hotel travel industry when:180d", "بازار جهانی"),
    ("ورود گردشگران بین‌المللی", "international tourist arrivals tourism industry when:180d", "روند جهانی"),
    ("سرمایه‌گذاری هتلداری", "international hotel groups hotel development tourism when:180d", "سرمایه‌گذاری جهانی"),
    ("حمل‌ونقل و سفر جهانی", "airline routes tourism travel industry destinations when:180d", "حمل‌ونقل جهانی"),
    ("هتل و پایداری", "hotel tourism sustainability destinations community when:180d", "گردشگری پایدار جهانی"),
    ("بازار گردشگری جهان", "tourism market destination management travel 2026 when:180d", "بازار جهانی"),
]
IR_TERMS = [
    "گردشگری","گردشگر","توریسم","اقامتگاه","بوم گردی","بوم‌گردی","میراث فرهنگی","میراث‌فرهنگی",
    "اکوتوریسم","طبیعت‌گردی","طبیعت گردی","صنایع دستی","صنایع‌دستی","هتلداری","هتل داری","هتل‌داری",
    "هتلداران","هتل‌داران","رزرو اقامت","گردشگرپذیر","جاذبه گردشگری","گردشگری سلامت","گردشگری شهری",
    "گردشگری دریایی","گردشگری ساحلی","توریستی","موزه","ثبت جهانی","قطار گردشگری","فرودگاه گردشگری",
    "گردشگری پایدار","گردشگری تاریخی","مسافرت داخلی","سفرهای داخلی","صنعت هتلداری"
]
EN_TERMS = [
    "tourism","tourist","hotel group","hotel occupancy","hotel market","hospitality industry",
    "hospitality market","travel demand","tourism industry","tourism market","hotel investment",
    "hotel development","travel industry","destination marketing","resort","tourist arrivals",
    "destination management","airline routes","international visitors"
]
BAD_TERMS = [
    "پاراوزنه","ملی پوش","ملی‌پوش","واحد مسکونی","هوش مصنوعی عکس","عکس دهه شصتی","فوتبال",
    "والیبال","بسکتبال","بورس","قیمت دلار","تیم ملی","آبرسانی","رزمایش بازسازی","عملیات میمک",
    "سازندگان و طراحان","صنعت ساختمان","قفل هوشمند"
]
HEAD = {"User-Agent": "VAEZI-INDUSTRY-RSS/2.0 (tourism editorial archive)"}
def clean(value):
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", value or "")).split())
def parse_date(value):
    for mode in (0, 1):
        try:
            d = parsedate_to_datetime(value) if mode == 0 else datetime.fromisoformat(value.replace("Z", "+00:00"))
            if d.tzinfo is None:
                d = d.replace(tzinfo=timezone.utc)
            return d.astimezone(timezone.utc).isoformat(timespec="seconds")
        except Exception:
            pass
    return ""
def text_child(node, names):
    for child in node.iter():
        if child.tag.split("}")[-1].lower() in names and child.text:
            return child.text
    return ""
def relevant(title, region, summary=""):
    t=(str(title or "")+" "+str(summary or "")).casefold().replace("‌"," ").replace("ك","ک").replace("ي","ی")
    bad=["پاراوزنه","ملی پوش","ملی‌پوش","واحد مسکونی","هوش مصنوعی عکس","عکس دهه شصتی","فوتبال","والیبال","بسکتبال","بورس","قیمت دلار","تیم ملی","آبرسانی","رزمایش بازسازی","عملیات میمک","سازندگان و طراحان","صنعت ساختمان","قفل هوشمند","پرستاری با تکیه بر قرآن","پرستاری","رزمایش","جنگی","عملیات نظامی","خبر ورزشی"]
    if any(x in t for x in bad): return False
    if region=="world":
        return any(x in t for x in ["tourism","tourist","hotel","hospitality","travel demand","accommodation","resort","destination management","airline routes","international visitors","visitor economy"])
    strong=["گردشگری","گردشگر","توریسم","اقامتگاه","بوم‌گردی","بوم گردی","میراث فرهنگی","میراث‌فرهنگی","اکوتوریسم","طبیعت‌گردی","طبیعت گردی","صنایع دستی","صنایع‌دستی","هتلداری","هتل‌داری","هتل داری","هتلداران","هتل‌داران","رزرو اقامت","گردشگرپذیر","جاذبه گردشگری","گردشگری سلامت","گردشگری شهری","گردشگری دریایی","گردشگری ساحلی","توریستی","موزه","قطار گردشگری","فرودگاه گردشگری","گردشگری پایدار","گردشگری تاریخی","مسافرت داخلی","سفرهای داخلی","صنعت هتلداری","هتل","روستای گردشگری","بازار اقامت","ضریب اشغال"]
    if any(x in t for x in strong): return True
    if "سفر" in t and any(x in t for x in ["مقصد گردشگری","اقامتگاه","جاذبه گردشگری","طبیعت‌گردی","طبیعت گردی","روستای گردشگری","ساحل","جزیره","میراث فرهنگی","بازدید از جاذبه","رزرو اقامت"]): return True
    return False
def quality(item):
    title=clean(item.get("title",""))
    summary=clean(item.get("summary",""))
    # Don't publish bare headlines; source excerpts may be concise but must carry information.
    if len(summary)<35: return False
    combined=(summary+" "+item.get("source","")+" "+item.get("sourceUrl","")).casefold()
    if any(x in combined for x in ["safariindia.com","sports news","football match"]): return False
    if summary.casefold().strip(" .-")==title.casefold().strip(" .-"): return False
    if re.search(r"https?://|www\\.",summary,re.I) and len(summary)<len(title)+40: return False
    return True
def category_for(title, region, default=""):
    t = title.casefold()
    if region == "world":
        if any(x in t for x in ["hotel","hospitality","occupancy"]): return "بازار جهانی"
        if any(x in t for x in ["airline","airport","flight","rail"]): return "حمل‌ونقل جهانی"
        return "روند جهانی"
    checks = [
        (["تسهیلات","سرمایه‌گذاری","سرمایه گذاری","تأمین مالی","تامین مالی"], "سرمایه‌گذاری"),
        (["اقامتگاه","هتل","هتلداری","ضریب اشغال","رزرو"], "اقامت و هتلداری"),
        (["پرواز","فرودگاه","قطار","راه‌آهن","حمل‌ونقل"], "حمل‌ونقل"),
        (["رویداد","همایش","نمایشگاه","جشنواره"], "رویدادها"),
        (["میراث","موزه","ثبت جهانی","یونسکو","تاریخی","کاروانسرا"], "میراث فرهنگی"),
        (["سلامت","درمانی"], "گردشگری سلامت"),
        (["اکوتوریسم","طبیعت‌گردی","پایدار","روستایی","بوم‌گردی"], "گردشگری پایدار"),
        (["فناوری","رزرو آنلاین","پلتفرم","دیجیتال"], "فناوری سفر"),
        (["وزارت","سند","قانون","سیاست"], "سیاست‌گذاری"),
    ]
    for needles, label in checks:
        if any(n in t for n in needles): return label
    return default or "بازار گردشگری"
def image_for(title, region, category):
    if region == "world": return "world"
    t = title.casefold()
    for terms, key in [
        (["تبریز","آذربایجان"],"isfahan"), (["گیلان","رشت","ماسوله","مازندران"],"rasht"),
        (["یزد","بادگیر"],"yazd"), (["شیراز","فارس","نصیرالملک"],"shiraz"),
        (["کیش","جزیره","ساحل","هرمزگان"],"kish"), (["قشم","دره ستارگان"],"qeshm"),
        (["تهران","آزادی"],"tehran"), (["تخت جمشید","مرودشت","پاسارگاد"],"persepolis"),
        (["کویر","شهداد","کلوت"],"desert"), (["اقامتگاه","هتل","رزرو"],"guesthouse"),
        (["اصفهان","نقش جهان"],"isfahan")
    ]:
        if any(x in t for x in terms): return key
    if category in ("اقامت و هتلداری","بازار اقامت","سرمایه‌گذاری"): return "guesthouse"
    return "isfahan"
def editorial_context(title, region, category):
    t = title.casefold()
    if region == "world":
        return "این نمونه برای رصد روند جهانی است؛ شرایط بازار، مقررات، امنیت، زیرساخت و ساختار سفر کشورها متفاوت است و نتیجه را نمی‌توان مستقیم به ایران تعمیم داد."
    if any(x in t for x in ("همایش","نمایشگاه","رویداد","جشنواره")):
        return "اعلام برنامه با اثبات برگزاری همهٔ بخش‌ها یا دستاورد نهایی یکسان نیست؛ برای جزئیات اجرایی، برگزارکننده و گزارش پس از رویداد را بررسی کنید."
    if any(x in t for x in ("تسهیلات","سرمایه‌گذاری","سرمایه گذاری","پروژه","بودجه")):
        return "رقم اعلام‌شده باید همراه با تاریخ و منبع نقل شود؛ برای سنجش اثر اقتصادی، میزان تخصیص و پرداخت واقعی و نتایج اجرایی نیز لازم است."
    if any(x in t for x in ("روستا","مقصد","میراث","تاریخی","جاذبه","موزه")):
        return "این خبر می‌تواند برای شناخت مقصد مفید باشد؛ اما اطلاعات متغیر مانند مسیر دسترسی، ساعات بازدید و امکانات را نزدیک سفر جداگانه کنترل کنید."
    return "این خلاصه بر پایهٔ توضیحات همراه گزارش تهیه شده است؛ برای جزئیات کامل، زمینه و اصلاحیه‌های احتمالی، منبع اصلی را باز کنید."
def enrich(item):
    title = clean(item.get("title", ""))
    summary = clean(item.get("summary", ""))
    if not item.get("category"):
        item["category"] = category_for(title, item.get("region", "iran"))
    item["image"] = item.get("image") or image_for(title, item.get("region", "iran"), item.get("category", ""))
    if item.get("region") == "world" and ("syria" in title.casefold() or "سوریه" in title):
        item["summary"] = "گروه‌های هتلداری بین‌المللی و منطقه‌ای در حال بررسی حضور یا توسعهٔ فعالیت در سوریه‌اند. دادهٔ دولتی نقل‌شده در گزارش رویترز برای نیمهٔ نخست ۲۰۲۶ حدود ۳٫۵۲ میلیون بازدیدکننده را نشان می‌دهد؛ در کنار این فرصت، زیرساخت آسیب‌دیده و نااطمینانی همچنان چالش‌اند."
        item["body"] = "گزارش رویترز می‌گوید شرکت‌هایی از جمله Accor و Wyndham فرصت‌های هتلداری در دمشق و مقصدهای ساحلی سوریه را بررسی می‌کنند و شرکت‌های منطقه‌ای نیز از طرح‌های بزرگ‌تر سخن گفته‌اند. داده‌های دولتی سوریه که در گزارش نقل شده، ۳٫۵۲ میلیون بازدیدکننده را برای نیمهٔ نخست ۲۰۲۶ نشان می‌دهد؛ بیش از ۲٫۱ میلیون نفر از این مجموع، سوری‌های مقیم خارج بوده‌اند.\n\nگزارش در کنار این چشم‌انداز، از آسیب زیرساخت‌ها، وضعیت امنیتی، محدودیت پرداخت الکترونیکی و اعتراض برخی جوامع محلی به طرح‌های بزرگ نیز می‌گوید. رشد تقاضا به‌تنهایی به معنی بازاری آماده و کم‌ریسک برای سرمایه‌گذاری نیست."
        item["context"] = editorial_context(title,"world",item.get("category",""))
    elif "تبریز" in title and ("میراث" in title or "هویت" in title):
        item["category"] = "میراث فرهنگی"
        item["body"] = "مدیرکل میراث فرهنگی، گردشگری و صنایع‌دستی آذربایجان‌شرقی از عملکرد شهرداری تبریز در احیای هویت تاریخی شهر تمجید کرده و طرح «هزار سال سرو و سروش» را فرصتی برای تقویت جایگاه تاریخی تبریز دانسته است. این نگاه، میراث شهری را نه‌فقط مجموعه‌ای از بناها، بلکه بخشی از روایت و هویت مقصد مطرح می‌کند.\n\nبرای سنجش اثر چنین برنامه‌هایی بر گردشگری، باید بعداً داده‌هایی مانند بازدیدکنندگان، رویدادهای اجراشده، نگهداشت بناها و مشارکت کسب‌وکارهای محلی بررسی شوند."
        item["context"] = "متن ایسنا ارزیابی مدیرکل و اشاره به طرح را نقل می‌کند؛ بودجه، زمان‌بندی اجرا یا آمار رشد گردشگر در همین گزیده ارائه نشده است."
    elif "کهنه‌ده" in title:
        item["category"] = "مقصدهای ایران"
        item["body"] = "گزارش مهر روستای کهنه‌ده در کرج را به‌عنوان مقصدی معرفی می‌کند که جذابیت آن تنها به منظرهٔ کوهستانی محدود نیست. نان سنتی، حلوای پنیر، محصولات باغی و مهارت‌های به‌جامانده از نسل‌های گذشته نیز بخش مهمی از تجربهٔ معرفی‌شده در گزارش‌اند.\n\nبرای مقصدهای روستایی، خوراک و مهارت محلی می‌توانند بخشی از روایت سفر باشند؛ اما معرفی مسئولانه باید به زندگی ساکنان، دسترسی، ظرفیت پذیرش و حفاظت از محیط روستا هم توجه کند."
        item["context"] = "خلاصهٔ منبع، جزئیات عملی مانند وضعیت جاده، ساعات فعالیت یا امکانات بازدید را مشخص نمی‌کند؛ پیش از برنامه‌ریزی این موارد را از منبع محلی بررسی کنید."
    elif "کرمان" in title and ("هتلداری" in title or "همایش" in title):
        item["category"] = "رویدادها"
        item["body"] = "طبق گزارش ایسنا، نخستین همایش و نمایشگاه هتلداری و صنایع وابسته کشور برای روزهای ۲۴ و ۲۵ مهر در کرمان و به میزبانی اتاق بازرگانی کرمان برنامه‌ریزی شده بود. گزارش به حضور معاون صنایع‌دستی و هنرهای سنتی وزارت میراث فرهنگی نیز اشاره دارد.\n\nچنین گردهمایی‌هایی می‌توانند فرصتی برای ارتباط میان هتل‌ها و تأمین‌کنندگان خدمات باشند؛ با این حال، گزیدهٔ خبری دربارهٔ تعداد شرکت‌کنندگان، محورهای کامل برنامه یا نتیجه‌های تجاری اطلاعات دقیقی نمی‌دهد."
        item["context"] = "این متن تاریخ و میزبانی اعلام‌شده در خبر را بازتاب می‌دهد؛ برای تعداد حاضران یا دستاوردهای قطعی، به گزارش پس از برگزاری نیاز است."
    elif item.get("kind") == "rss":
        if not item.get("body") or "خبرخوان RSS کشف شده" in item.get("body",""):
            item["body"] = summary + "\n\n" + editorial_context(title,item.get("region","iran"),item.get("category",""))
        item.setdefault("context",editorial_context(title,item.get("region","iran"),item.get("category","")))
    item["archived"] = item.get("archived", False) or (
        bool(item.get("publishedAt")) and parse_date(item.get("publishedAt")) != "" and
        datetime.fromisoformat(parse_date(item.get("publishedAt")).replace("Z","+00:00")) < datetime.now(timezone.utc)-timedelta(days=45)
    )
    return item
def parse_feed(payload,source,region,category,google=False):
    root=ET.fromstring(payload);items=[]
    seen=0;relevance_rejects=0;quality_rejects=0
    context_ir=["اقامت","اقامتگاه","هتل","مسافر","گردش","مقصد","روستا","استان","میراث","تاریخی","موزه","بازدید","باغ","پارک","طبیعت","جنگل","ساحل","جزیره","کویر","فرودگاه","پرواز","قطار","تور","دهکده","رستوران","خوراک","محلی","جاذبه","رزرو","مهمان","مسیر گردشگری","گردشگر"]
    context_world=["tourism","tourist","hotel","hospitality","travel","visitor","resort","destination","airline","accommodation","cruise","tour operator","hotel group","hotel investment"]
    for node in root.iter():
        if node.tag.split("}")[-1].lower() not in ("item","entry"):continue
        seen+=1
        title=clean(text_child(node,{"title"}));link=text_child(node,{"link"})
        if not link:
            for child in node:
                if child.tag.split("}")[-1].lower()=="link" and child.attrib.get("href"):
                    link=child.attrib["href"];break
        link=(link or "").strip()
        summary=clean(text_child(node,{"description","summary","content"}))
        if not title or not link.startswith(("http://","https://")):continue
        text_for_check=(title+" "+summary).casefold()
        bad=["پرستاری با تکیه بر قرآن","پرستاری","رزمایش بازسازی","عملیات میمک","سازندگان و طراحان","صنعت ساختمان","قفل هوشمند","فوتبال","والیبال","بسکتبال","پاراوزنه","تیم ملی","بورس","قیمت دلار","safariindia.com"]
        if any(term in text_for_check for term in bad):continue
        strict=relevant(title,region,summary)
        if not strict:
            # Google News RSS is a topic-specific search query. Allow a longer contextual excerpt
            # where the headline doesn't repeat words such as "tourism" but clearly describes travel.
            terms=context_world if region=="world" else context_ir
            if not google or len(summary)<65 or not any(term in text_for_check for term in terms):
                relevance_rejects+=1;continue
        published=parse_date(text_child(node,{"pubdate","published","updated","date"}))
        if not published:continue
        src=""
        for child in node:
            if child.tag.split("}")[-1].lower()=="source" and child.text:src=clean(child.text);break
        if not src or src.casefold() in ("بدون منبع","unknown"):src=source
        digest=hashlib.sha1(link.encode()).hexdigest()[:14]
        item={"id":"rss-"+digest,"title":title,"summary":summary[:420],"source":src,"sourceUrl":link,"publishedAt":published,"region":region,"category":category_for(title,region,category),"image":image_for(title,region,category),"kind":"rss","contentType":"news"}
        if not quality(item):
            quality_rejects+=1;continue
        items.append(enrich(item))
    print("FEED",source,"raw",seen,"kept",len(items),"relevance_filtered",relevance_rejects,"quality_filtered",quality_rejects)
    return items
def fetch(url):
    with urlopen(Request(url,headers=HEAD),timeout=18) as response:return response.read(2_000_000)
def google(query,region):
    params="hl=en-US&gl=US&ceid=US:en" if region=="world" else "hl=fa&gl=IR&ceid=IR:fa"
    return fetch("https://news.google.com/rss/search?q="+quote(query)+"&"+params)
def dedupe(rows):
    seen=set();result=[]
    for item in sorted(rows,key=lambda x:x.get("publishedAt",""),reverse=True):
        key="".join(ch for ch in item.get("title","").casefold() if ch.isalnum())
        if key and key not in seen:seen.add(key);result.append(item)
    return result
def make_feed(items):
    now=datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT");entries=[]
    for item in items[:200]:
        try:pub=datetime.fromisoformat(item.get("publishedAt","").replace("Z","+00:00")).strftime("%a, %d %b %Y %H:%M:%S GMT")
        except Exception:pub=now
        entries.append("<item><title>"+escape(item.get("title",""))+"</title><link>"+escape(item.get("sourceUrl",""))+"</link><guid isPermaLink=\"false\">"+escape(item.get("id",""))+"</guid><pubDate>"+escape(pub)+"</pubDate><description>"+escape(item.get("summary","")[:500])+"</description></item>")
    return '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>VAEZI INDUSTRY | گردشگری ایران</title><link>https://mohammadrezavaezi56.github.io/vaezi-industry/</link><description>خبرهای گردشگری ایران و گزیده‌ای از جهان</description><language>fa</language><lastBuildDate>'+now+'</lastBuildDate>'+''.join(entries)+'</channel></rss>\n'
def main():
    seeds=json.loads(SEEDS.read_text(encoding="utf-8")).get("items",[])
    old=json.loads(NEWS.read_text(encoding="utf-8")) if NEWS.exists() else {"items":[]}
    old_items=old if isinstance(old,list) else old.get("items",[])
    previous=[enrich(x) for x in old_items if x.get("kind")=="rss" and relevant(x.get("title",""),x.get("region","iran"),x.get("summary","")) and quality(x)]
    fresh_ir=[];fresh_world=[];warnings=[];success=0
    tasks=[]
    for name,url in DIRECT:tasks.append(("direct",name,url,"iran","اخبار گردشگری"))
    for name,query,category in IR_QUERIES:tasks.append(("google",name,query,"iran",category))
    for name,query,category in WORLD_QUERIES:tasks.append(("google",name,query,"world",category))
    def run_task(task):
        kind,name,value,region,category=task
        payload=fetch(value) if kind=="direct" else google(value,region)
        return task,parse_feed(payload,name,region,category,kind=="google")
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futuremap={pool.submit(run_task,task):task for task in tasks}
        for future in concurrent.futures.as_completed(futuremap):
            task=futuremap[future]
            try:
                result,rows=future.result()
                success+=1
                if result[3]=="world":fresh_world.extend(rows)
                else:fresh_ir.extend(rows)
                print("OK",result[1],"accepted",len(rows))
            except Exception as error:
                warnings.append(task[1]+": "+str(error))
                print("WARN",task[1],error)
    seeds=[enrich(x) for x in seeds]
    curated_ir=[x for x in seeds if x.get("region")!="world"]
    curated_world=[x for x in seeds if x.get("region")=="world"]
    iran=dedupe(curated_ir+[x for x in previous if x.get("region")!="world"]+fresh_ir)
    rss_world=dedupe([x for x in previous if x.get("region")=="world"]+fresh_world)
    curated_ids={x.get("id") for x in curated_world}
    world=curated_world+[x for x in rss_world if x.get("id") not in curated_ids]
    world_limit=min(10,max(1,round(len(iran)/9))) if world else 0
    items=iran[:180]+world[:world_limit]
    if len(items)<100:
        # Never fabricate articles merely to meet a count. Preserve all quality source-backed items and expose the shortfall in logs.
        print("WARNING: only",len(items),"quality items available; expand sources rather than duplicating headlines.")
    items.sort(key=lambda x:x.get("publishedAt",""),reverse=True)
    payload={"updatedAt":datetime.now(timezone.utc).isoformat(timespec="seconds"),"mix":{"iranTargetPercent":90,"worldTargetPercent":10},"feedStatus":{"configuredFeeds":len(tasks),"successfulFeeds":success,"warnings":warnings},"items":items}
    NEWS.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    FEED.write_text(make_feed(items),encoding="utf-8")
    print("Published",len(items),"articles; Iran",sum(x.get("region")!="world" for x in items),"World",sum(x.get("region")=="world" for x in items))
if __name__=="__main__":
    main()
