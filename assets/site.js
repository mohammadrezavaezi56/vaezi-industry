(()=>{'use strict';
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>Array.from(r.querySelectorAll(s));
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const photos={
'iran-panorama':'assets/images/photos/iran-panorama.jpg',
isfahan:'assets/images/photos/isfahan.jpg',
rasht:'assets/images/photos/rasht.jpg',
yazd:'assets/images/photos/yazd.jpg',
shiraz:'assets/images/photos/shiraz.jpg',
kish:'assets/images/photos/kish.jpg',
qeshm:'assets/images/photos/qeshm.jpg',
tehran:'assets/images/photos/tehran.jpg',
persepolis:'assets/images/photos/persepolis.jpg',
desert:'assets/images/photos/desert.jpg',
guesthouse:'assets/images/photos/guesthouse.jpg',
world:'assets/images/photos/guesthouse.jpg'
};
const photoAlt={
'iran-panorama':'ترکیبی از عکس‌های واقعی مقصدهای ایران',
isfahan:'میدان نقش‌جهان اصفهان؛ عکس از Armin Dadvand / Wikimedia Commons',
rasht:'ماسوله، گیلان؛ عکس از Mojtaba Matboyi / Wikimedia Commons',
yazd:'بادگیرهای یزد؛ عکس از Ms96 / Wikimedia Commons',
shiraz:'مسجد نصیرالملک شیراز؛ عکس از Faraz Ahanin / Wikimedia Commons',
kish:'ساحل کیش؛ عکس از Ivan Mlinaric / Wikimedia Commons',
qeshm:'درهٔ ستارگان قشم؛ عکس از Qeshmnil / Wikimedia Commons',
tehran:'برج آزادی تهران؛ عکس از Mostafa Meraji / Wikimedia Commons',
persepolis:'ستون‌های تخت جمشید؛ عکس از Abbas Sarhadi / Wikimedia Commons',
desert:'کلوت‌های شهداد؛ عکس از Salehi1990mohsen / Wikimedia Commons',
guesthouse:'اقامتگاه سنتی یزد؛ عکس آرشیوی از Wikimedia Commons',
world:'تصویر نمایشی از اقامتگاه؛ نه عکس مستند از خبر جهانی'
};
const fallbackItems=[{"id":"iran-recovery-policy","title":"سند بازآفرینی گردشگری ایران در دورهٔ پساجنگ ابلاغ شد","summary":"گزارش منتشرشده در ۲۲ مهر می‌گوید سند راهبردی جدید بر سه خوشهٔ گردشگری طبیعت‌محور و جامعه‌محور، سلامت و میراث فرهنگی‌ـ‌تاریخی تأکید دارد.","body":"به گزارش عصر گردشگری به نقل از مهر، معاون گردشگری از ابلاغ سندی برای هماهنگی اقدامات ملی و استانی و بازتعریف مزیت‌های رقابتی گردشگری ایران خبر داده است. ابلاغ سند به‌تنهایی به معنای تحقق نتایج نیست؛ باید اجرای برنامه‌ها و گزارش‌های دوره‌ای بعدی بررسی شود.","source":"عصر گردشگری · به نقل از مهر","sourceUrl":"https://asregardeshgari.com/cultural-heritage-news/371345/","publishedAt":"2026-10-14","region":"iran","category":"سیاست‌گذاری","image":"isfahan","manual":true},{"id":"alborz-tourism-exam","title":"آغاز ثبت‌نام آزمون جامع گردشگری البرز از ۲۵ مهر اعلام شد","summary":"در فهرست مطالب ۲۲ مهرِ عصر گردشگری، زمان آغاز ثبت‌نام آزمون جامع گردشگری البرز ۲۵ مهر اعلام شده است؛ متقاضیان باید اطلاعیهٔ نهاد برگزارکننده را کنترل کنند.","body":"این خبر زمان اعلام‌شده در منبع را بازتاب می‌دهد و جایگزین اطلاعیهٔ رسمی برگزارکننده نیست. شرایط ثبت‌نام، مدارک و زمان‌بندی نهایی را از مرجع مربوط تأیید کنید.","source":"عصر گردشگری","sourceUrl":"https://asregardeshgari.com/","publishedAt":"2026-10-14","region":"iran","category":"آموزش گردشگری","image":"guesthouse","manual":true},{"id":"tourism-credit-fund","title":"گزارش: ۴۰ همت تسهیلات برای گردشگری و صنایع‌دستی در نظر گرفته شده است","summary":"گزارش‌های منتشرشده در ۲۰ مهر از درنظرگرفتن بیش از ۴۰ همت تسهیلات برای گردشگری و صنایع‌دستی خبر می‌دهند؛ رقم اعلامی با تسهیلات پرداخت‌شده یکسان نیست.","body":"این رقم به‌عنوان ظرفیت یا تسهیلات درنظرگرفته‌شده گزارش شده است. برای ارزیابی اثر واقعی بر کسب‌وکارها باید جزئیات تخصیص، شرایط دسترسی، میزان پرداخت و گزارش‌های رسمی تکمیلی در دسترس باشد.","source":"بازنشر خبر ایرنا / باشگاه خبرنگاران","sourceUrl":"https://www.collector.com.tr/1020504527","publishedAt":"2026-10-12","region":"iran","category":"سرمایه‌گذاری","image":"guesthouse","manual":true},{"id":"tourism-projects-construction","title":"گزارش: بیش از ۳ هزار پروژهٔ گردشگری در حال ساخت است","summary":"یک گزارش بازنشرشده به نقل از وزیر میراث‌فرهنگی از ۳٬۰۱۷ پروژه در ۳۱ استان و سرمایه‌گذاری اعلام‌شدهٔ ۱٬۳۰۰ همت خبر می‌دهد.","body":"این ارقام همان‌طور که در گزارش بازنشرشده آمده نقل می‌شوند؛ «در حال ساخت» با پروژهٔ تکمیل‌شده یا آمادهٔ بهره‌برداری تفاوت دارد. برای استفادهٔ پژوهشی باید متن منبع و تاریخ انتشار بررسی شود.","source":"ویستا · بازنشر خبر","sourceUrl":"https://vista.ir/2610/218/ptptf/%D9%88%D8%B2%DB%8C%D8%B1-%D9%85%DB%8C%D8%B1%D8%A7%D8%AB-%D9%81%D8%B1%D9%87%D9%86%DA%AF%DB%8C-%D9%88-%DA%AF%D8%B1%D8%AF%D8%B4%DA%AF%D8%B1%DB%8C-%D8%A8%DB%8C%D8%B4-%D8%A7%D8%B2-%DB%B3-%D9%87%D8%B2%D8%A7%D8%B1-%D9%BE%D8%B1%D9%88%DA%98%D9%87-%DA%AF%D8%B1%D8%AF%D8%B4%DA%AF%D8%B1%DB%8C-%D8%AF%D8%B1-%DA%A9%D8%B4%D9%88%D8%B1-%D8%AF%D8%B1%D8%AD%D8%A7%D9%84-%D8%B3%D8%A7%D8%AE%D8%AA-%D8%A7%D8%B3%D8%AA","publishedAt":"2026-10-08","region":"iran","category":"زیرساخت","image":"yazd","manual":true},{"id":"iran-hotel-occupancy-september","title":"رصد اشغال اقامتگاه‌ها در شهریور؛ تفاوت محسوس میان استان‌های شمالی","summary":"گزارش ۷ مهر تسنیم از ضریب اشغال بالا در گیلان، مازندران و اردبیل در شهریور خبر می‌دهد؛ این شاخص به همان بازهٔ زمانی محدود است.","body":"اعداد این گزارش نباید به‌عنوان نرخ فعلی اشغال یا پیش‌بینی فصل بعد استفاده شوند. برای تحلیل بازار باید ظرفیت موجود، طول اقامت، ترکیب سفرها و دادهٔ ماه‌های دیگر نیز بررسی شود.","source":"خبرگزاری تسنیم","sourceUrl":"https://www.tasnimnews.ir/fa/service/1416/%D8%B3%D9%81%D8%B1","publishedAt":"2026-09-29","region":"iran","category":"بازار اقامت","image":"rasht","manual":true},{"id":"iran-south-events","title":"طرح «مهر جنوب»؛ برنامه‌ریزی برای بیش از ۶۵۰ رویداد گردشگری","summary":"گزارش بازنشرشده به نقل از مهر از برنامه‌ریزی بیش از ۶۵۰ رویداد در طول مهر برای معرفی ظرفیت‌های گردشگری جنوب ایران خبر داده است.","body":"عدد اعلامی برنامهٔ برگزاری است، نه تأیید اجرای همهٔ رویدادها یا میزان استقبال. برای سفر به یک رویداد مشخص، زمان، مکان و وضعیت برگزاری را از برگزارکننده بررسی کنید.","source":"بازنشر خبر مهر","sourceUrl":"https://wona.ir/news/29h842nxm0/","publishedAt":"2026-09-22","region":"iran","category":"رویدادها","image":"kish","manual":true},{"id":"iran-coitm-2026","title":"حضور ایران در بازار گردشگری چین؛ فرصت معرفی مسیرهای فرهنگی","summary":"اطلاعیهٔ برگزارکنندهٔ COITM 2026 به حضور عرضه‌کنندگان و ظرفیت معرفی مقصدهای فرهنگی و تجاری در بازار چین اشاره می‌کند.","body":"این مطلب بازنویسی اطلاعیهٔ برگزارکننده است. از خود اطلاعیه نمی‌توان تعداد گردشگران جذب‌شده یا ارزش قراردادها را نتیجه گرفت؛ اثر رویداد باید با گزارش‌های بعدی بررسی شود.","source":"COITM · برگزارکننده","sourceUrl":"https://www.coitm.cn/en/COITM-News97","publishedAt":"2026-09-28","region":"iran","category":"بازارهای بین‌المللی","image":"shiraz","manual":true},{"id":"karon-waterfront-archive","title":"آرشیو: برنامهٔ توسعهٔ گردشگری ساحلی در حاشیهٔ کارون","summary":"گزارشی در آذر ۱۴۰۴ دربارهٔ برنامهٔ ساماندهی بخشی از ساحل کارون با هدف ایجاد مقصد گردشگری آبی منتشر شده بود.","body":"این گزارش آرشیوی است؛ اعلام برنامه معادل تکمیل پروژه نیست و وضعیت پیشرفت آن باید با منبع تازه‌تر بررسی شود.","source":"خبرگزاری مهر · آرشیو","sourceUrl":"https://www.mehrnews.com/news/6697518/","publishedAt":"2025-12-21","region":"iran","category":"زیرساخت","image":"kish","manual":true,"archived":true},{"id":"world-dubai-hotel-market","title":"نگاه جهانی: گزارش رویترز از بازیابی تدریجی اشغال هتل‌های دبی","summary":"رویترز در ۲۱ سپتامبر گزارش داد ضریب اشغال هتل‌های Emaar در دبی به حدود ۶۰٪ رسیده بود؛ هنوز پایین‌تر از سطح پیش از بحران و همراه با پیش‌بینی شرکت برای بازیابی تدریجی.","body":"این گزارش فقط وضعیت اعلام‌شده از سوی Emaar در سپتامبر ۲۰۲۶ را توصیف می‌کند؛ نه دادهٔ جاری همهٔ هتل‌های دبی. این نمونهٔ جهانی برای مقایسهٔ صنعت است و مستقیماً قابل تعمیم به ایران نیست.","source":"Reuters","sourceUrl":"https://www.reuters.com/world/middle-east/emaar-expects-return-pre-war-occupancy-levels-dubai-hotels-next-12-months-2026-09-21/","publishedAt":"2026-09-21","region":"world","category":"روند جهانی","image":"world","manual":true}];
let items=fallbackItems;

async function load(){
  const statuses=$$('[data-news-status]');
  const setStatus=message=>statuses.forEach(el=>{el.textContent=message});
  try{
    const response=await fetch('news.json?refresh=1',{cache:'no-store',headers:{'Accept':'application/json'}});
    if(!response.ok)throw new Error('خبرخوان پاسخ '+response.status+' برگرداند');
    const payload=await response.json();
    const rows=Array.isArray(payload)?payload:(Array.isArray(payload.items)?payload.items:[]);
    const valid=rows.filter(n=>n&&n.id&&n.title&&String(n.sourceUrl||n.link||'').startsWith('http'));
    if(!valid.length)throw new Error('فهرست خبرها خالی یا نامعتبر است');
    items=valid;
    let updated='زمان بازبینی مشخص نیست';
    if(payload.updatedAt){
      const stamp=new Date(payload.updatedAt);
      if(!Number.isNaN(stamp.getTime()))updated=new Intl.DateTimeFormat('fa-IR',{dateStyle:'medium',timeStyle:'short'}).format(stamp);
    }
    setStatus('آخرین به‌روزرسانی آرشیو: '+updated+' · '+new Intl.NumberFormat('fa-IR').format(valid.length)+' مطلب');
  }catch(error){
    items=fallbackItems;
    setStatus('نسخهٔ پشتیبان نمایش داده شد؛ اتصال آرشیو تازه در دسترس نیست.');
    console.warn('VAEZI INDUSTRY: news.json could not be loaded; fallback items are shown.',error);
  }
}
function safeUrl(s){try{let u=new URL(s,location.href);return ['http:','https:'].includes(u.protocol)?u.href:'#'}catch{return '#'}}
function dateText(n){if(n.displayDate)return n.displayDate;if(!n.publishedAt)return 'تاریخ در منبع مشخص نشده';let d=new Date(n.publishedAt);return isNaN(d)?n.publishedAt:new Intl.DateTimeFormat('fa-IR',{dateStyle:'medium'}).format(d)}
function scene(n){return Object.hasOwn(photos,n)?n:'iran-panorama'}
function shortExcerpt(value,max=235){let text=String(value||'').trim();return text.length>max?text.slice(0,max-1).trimEnd()+'…':text}
function card(n){
 let pic=scene(n.image),arch=n.archived||/آرشیو/.test(n.title),region=n.region==='world'?'جهان':'ایران';
 let alt=photoAlt[pic]||'عکس آرشیوی مرتبط با موضوع خبر';
 let summary=shortExcerpt(n.summary||n.body||'برای جزئیات بیشتر گزارش اصلی را بخوانید.');
 return '<article class="news-card"><div class="cover" style="background-image:url(\'assets/images/'+pic+'.svg\')"><img loading="lazy" decoding="async" src="'+esc(photos[pic]||'')+'" alt="'+esc(alt)+'" title="'+esc(alt)+'" onerror="this.style.display=\'none\'"></div><div class="card-body"><span class="tag '+(n.region==='world'?'world':'')+'">'+region+' · '+esc(n.category||'گردشگری')+'</span><h3><a href="article.html?id='+encodeURIComponent(n.id)+'">'+esc(n.title)+'</a></h3><span class="summary-label">خلاصهٔ مطلب</span><p class="card-summary">'+esc(summary)+'</p><div class="card-meta"><span>'+esc(dateText(n))+'</span><b>'+esc(n.source||'منبع')+(arch?' · آرشیو':'')+'</b></div><div class="card-actions"><a class="mini-btn" href="article.html?id='+encodeURIComponent(n.id)+'">متن کامل ←</a><a class="text-link" href="'+esc(safeUrl(n.sourceUrl||n.link||'#'))+'" target="_blank" rel="noopener noreferrer">منبع اصلی ↗</a></div></div></article>'
}
function latest(){ $$('[data-latest-news]').forEach(m=>{let arr=items.slice().sort((a,b)=>String(b.publishedAt||'').localeCompare(String(a.publishedAt||''))).slice(0,6);m.innerHTML=arr.map(card).join('')||'<p>خبر تازه‌ای موجود نیست.</p>'})}
function newsPage(){
 let grid=$('[data-news-list]');if(!grid)return;
 let inp=$('[data-news-search]'),count=$('[data-count]'),empty=$('[data-empty]'),pager=$('[data-pagination]');
 let params=new URLSearchParams(location.search),region=params.get('region')||'all',category='all',page=1;
 if(inp)inp.value=params.get('q')||'';
 const pageSize=18;
 const norm=s=>String(s||'').toLocaleLowerCase('fa').replace(/ي/g,'ی').replace(/ك/g,'ک');
 function render(){
  let q=norm(inp?.value.trim());
  let arr=items.filter(n=>(region==='all'||n.region===region)&&(!q||norm([n.title,n.summary,n.body,n.context,n.source,n.category].join(' ')).includes(q))&&(category==='all'||norm(n.category).includes(norm(category))));
  arr.sort((a,b)=>String(b.publishedAt||'').localeCompare(String(a.publishedAt||'')));
  const pages=Math.max(1,Math.ceil(arr.length/pageSize));page=Math.min(page,pages);
  const start=(page-1)*pageSize,end=Math.min(start+pageSize,arr.length);
  grid.innerHTML=arr.slice(start,end).map(card).join('');
  if(count)count.textContent=arr.length?('نمایش '+new Intl.NumberFormat('fa-IR').format(start+1)+' تا '+new Intl.NumberFormat('fa-IR').format(end)+' از '+new Intl.NumberFormat('fa-IR').format(arr.length)+' مطلب'):'مطلبی با این فیلتر پیدا نشد';
  if(empty)empty.hidden=arr.length>0;
  if(pager){
   if(pages<=1){pager.innerHTML='';pager.hidden=true}
   else{pager.hidden=false;pager.innerHTML='<button class="page-button" data-page="'+Math.max(1,page-1)+'" '+(page===1?'disabled':'')+'>قبلی</button><span class="page-status">صفحهٔ '+new Intl.NumberFormat('fa-IR').format(page)+' از '+new Intl.NumberFormat('fa-IR').format(pages)+'</span><button class="page-button" data-page="'+Math.min(pages,page+1)+'" '+(page===pages?'disabled':'')+'>بعدی</button>';$$('[data-page]',pager).forEach(btn=>btn.addEventListener('click',()=>{page=Number(btn.dataset.page)||1;render();grid.scrollIntoView({behavior:'smooth',block:'start'})}));}
  }
 }
 inp?.addEventListener('input',()=>{page=1;render()});
 $$('[data-region]').forEach(btn=>{btn.classList.toggle('active',btn.dataset.region===region);btn.addEventListener('click',()=>{region=btn.dataset.region;page=1;$$('[data-region]').forEach(x=>x.classList.toggle('active',x===btn));render()})});
 $$('[data-category]').forEach(btn=>btn.addEventListener('click',()=>{category=btn.dataset.category;page=1;$$('[data-category]').forEach(x=>x.classList.toggle('active',x===btn));render()}));
 render()
}
const cities={isfahan:{name:'اصفهان',sub:'معماری، میدان‌ها و هنر شهری',image:'isfahan',intro:'اصفهان برای علاقه‌مندان معماری، هنرهای سنتی، میدان‌های تاریخی و تجربهٔ پیاده‌روی شهری مقصدی پربار است.',tips:['ساعت و محدودیت بازدید بناها را در روز سفر کنترل کن.','زمانی برای بازارها و صنایع‌دستی کنار بگذار.','فاصله و مسیر پیاده را میان جاذبه‌ها در نظر بگیر.'],stay:'موقعیت اقامت را نسبت به مرکز تاریخی، حمل‌ونقل و برنامهٔ بازدید بسنج.'},rasht:{name:'رشت و گیلان',sub:'طبیعت، خوراک و روستا',image:'rasht',intro:'رشت می‌تواند پایگاهی برای شناخت خوراک محلی، بازار شهری و سفرهای پیرامونی به طبیعت و روستاهای گیلان باشد.',tips:['برای تغییرات هوا و بارندگی برنامهٔ جایگزین داشته باش.','برای مسیرهای طبیعی از راهنمای محلی و مسیر مجاز استفاده کن.','به ظرفیت مقصد و زندگی ساکنان روستا احترام بگذار.'],stay:'فاصله تا بافت شهری و مسیرهای پیرامونی را با برنامهٔ سفر هماهنگ کن.'},yazd:{name:'یزد',sub:'بافت خشتی و بادگیرها',image:'yazd',intro:'یزد مقصدی مناسب برای شناخت معماری سازگار با اقلیم، کوچه‌های تاریخی و زندگی در مناطق خشک است.',tips:['به حریم خانه‌ها و آرامش محله توجه کن.','ساعات رسمی بازدید جاذبه‌ها را بررسی کن.','آب و استراحت در ساعات گرم را در برنامه بگنجان.'],stay:'دربارهٔ دسترسی خودرو، پله‌ها و امکانات اقامتگاه تاریخی از قبل سؤال کن.'},shiraz:{name:'شیراز',sub:'باغ، شعر و میراث فرهنگی',image:'shiraz',intro:'شیراز ترکیبی از باغ‌ها، میراث ادبی، معماری و بازدید از محوطه‌های تاریخی پیرامون شهر را فراهم می‌کند.',tips:['برای باغ‌ها و اماکن تاریخی زمان کافی کنار بگذار.','برای مرودشت و تخت جمشید مسیر رفت‌وبرگشت را جدا برنامه‌ریزی کن.','قواعد عکاسی و ساعت بازدید را بررسی کن.'],stay:'محل اقامت را با توجه به فاصله از جاذبه‌ها و روش جابه‌جایی انتخاب کن.'},kish:{name:'کیش',sub:'ساحل و تفریحات دریایی',image:'kish',intro:'در کیش، تجربهٔ سفر به حمل‌ونقل، شرایط دریا، فاصلهٔ اقامتگاه تا فعالیت‌ها و هزینه‌های جانبی وابسته است.',tips:['شرایط دریا و مجازبودن فعالیت‌های آبی را بررسی کن.','جزئیات پرواز یا مسیر دریایی را از ارائه‌دهنده تأیید بگیر.','قیمت نهایی فعالیت‌ها را پیش از پرداخت روشن کن.'],stay:'فاصله تا ساحل و شیوهٔ رفت‌وآمد را کنار قیمت بسنج.'},desert:{name:'کویر مرکزی',sub:'منظره، آسمان و سکوت',image:'desert',intro:'سفر کویری نیازمند برنامه‌ریزی دقیق، شناخت مسیر و آمادگی برای تغییرات آب‌وهواست؛ خودسرانه وارد مسیر دورافتاده نشو.',tips:['با راهنمای معتبر و برنامهٔ مشخص حرکت کن.','آب، ارتباط اضطراری و تجهیزات مناسب آماده کن.','به پوشش گیاهی و محیط حساس آسیب نزن.'],stay:'امکانات، فاصله و دسترسی واقعی اقامتگاه را از میزبان یا مرجع رزرو تأیید کن.'},tehran:{name:'تهران',sub:'گردشگری شهری و فرهنگی',image:'tehran',intro:'تهران در کنار مرکز اقتصادی، ظرفیت‌های موزه‌ای، معماری، پارک‌ها، خوراک و گردشگری شهری دارد.',tips:['برنامه را با ترافیک و حمل‌ونقل عمومی هماهنگ کن.','ساعات موزه‌ها را از منبع رسمی بررسی کن.','فاصلهٔ واقعی و زمان جابه‌جایی را در نظر بگیر.'],stay:'انتخاب محل اقامت نزدیک مسیرهای برنامه‌ریزی‌شده زمان رفت‌وآمد را کم می‌کند.'},qeshm:{name:'قشم',sub:'ژئوپارک، ساحل و فرهنگ جنوب',image:'qeshm',intro:'قشم چشم‌اندازهای زمین‌شناختی، ساحل و فرهنگ محلی جنوب را کنار هم دارد؛ بازدید باید با حفاظت از طبیعت همراه باشد.',tips:['وضعیت مسیر و راهنمای محلی را بررسی کن.','از ورود به مناطق حساس یا غیرمجاز خودداری کن.','زمان جابه‌جایی بین جاذبه‌ها را واقع‌بینانه بسنج.'],stay:'محل اقامت را نسبت به مسیرها و نیاز به وسیلهٔ رفت‌وآمد انتخاب کن.'},persepolis:{name:'تخت جمشید و مرودشت',sub:'میراث باستانی و تاریخ',image:'persepolis',intro:'بازدید از محوطه‌های باستانی به زمان کافی، رعایت قواعد حفاظت و بررسی ساعت رسمی بازدید نیاز دارد.',tips:['از لمس یا بالا رفتن از بخش‌های ممنوع خودداری کن.','برای راهنمایی تاریخی از منابع رسمی کمک بگیر.','آب و محافظت در برابر آفتاب را فراموش نکن.'],stay:'اگر از شیراز سفر می‌کنی، رفت‌وبرگشت و زمان بازدید را جدا برنامه‌ریزی کن.'}};
function destination(){let el=$('[data-destination]');if(!el)return;let key=new URLSearchParams(location.search).get('city')||'isfahan',c=cities[key];if(!c){el.innerHTML='<div class="article"><h1>مقصد پیدا نشد</h1><a class="btn btn-dark" href="destinations.html">بازگشت</a></div>';return}document.title=c.name+' | VAEZI INDUSTRY';el.innerHTML='<article class="detail"><div class="detail-hero" style="background-image:url(\'assets/images/'+esc(c.image)+'.svg\')"><div><span class="tag">راهنمای مقصد ایران</span><h1>'+esc(c.name)+'</h1><p>'+esc(c.sub)+'</p></div></div><div class="detail-body"><div><h2>نگاه کلی</h2><p>'+esc(c.intro)+'</p><h2 style="margin-top:15px">نکته‌های برنامه‌ریزی</h2><ul>'+c.tips.map(t=>'<li>'+esc(t)+'</li>').join('')+'</ul><p>شرایط آب‌وهوا، مسیر و ساعت فعالیت در روز سفر از مرجع مربوط بررسی شود.</p></div><aside class="detail-side"><h2>اقامت و دسترسی</h2><p>'+esc(c.stay)+'</p><a href="platforms.html">شناخت پلتفرم‌های اقامت ←</a><a href="travel-guide.html">راهنمای عمومی سفر ←</a><a href="news.html">خبرهای گردشگری ←</a></aside></div></article>'}
function paragraphs(value){
 return String(value||'').split(/\n\s*\n/).map(p=>p.trim()).filter(Boolean)
   .map(p=>'<p>'+esc(p).replace(/\n/g,' ')+'</p>').join('');
}
function defaultContext(n){
 const t=String(n.title||'');
 if(n.region==='world')return 'این نمونه به یک بازار خارجی مربوط است. برای نتیجه‌گیری دربارهٔ ایران، باید داده‌های هم‌دوره و قابل‌مقایسه در دسترس باشد.';
 if(/همایش|نمایشگاه|رویداد/.test(t))return 'اعلام برنامه به معنای اثبات نتیجهٔ نهایی نیست؛ آمار حضور، قراردادها و اثر اقتصادی پس از رویداد باید جداگانه بررسی شوند.';
 if(/پروژه|سرمایه‌گذاری|تسهیلات/.test(t))return 'ارزیابی اثر این خبر به وضعیت اجرا، تخصیص واقعی منابع و شاخص‌های قابل‌سنجش نیاز دارد؛ عدد اعلام‌شده به‌تنهایی نتیجهٔ نهایی را نشان نمی‌دهد.';
 if(/روستا|مقصد|میراث|تاریخی/.test(t))return 'برای برنامه‌ریزی سفر، جزئیات روزآمد دسترسی، امکانات، ساعت بازدید و محدودیت‌های محلی را نیز بررسی کنید.';
 return 'این خلاصه بر پایهٔ اطلاعات قابل‌مشاهده در منبع پیوندشده تهیه شده است؛ برای جزئیات کامل و اصلاحیه‌های احتمالی، گزارش اصلی را بخوانید.';
}
function article(){
 const el=$('[data-article]');if(!el)return;
 const id=new URLSearchParams(location.search).get('id');
 const n=items.find(x=>String(x.id)===id);
 if(!n){el.innerHTML='<h1>مطلب پیدا نشد</h1><p>ممکن است مطلب از فید حذف شده باشد.</p><a class="btn btn-dark" href="news.html">بازگشت به اخبار</a>';return}
 document.title=n.title+' | VAEZI INDUSTRY';
 const pic=scene(n.image);
 const region=n.region==='world'?'جهان':'ایران';
 const context=n.context||n.editorialNote||defaultContext(n);
 el.innerHTML=
  '<div class="cover article-cover" style="height:220px;background-image:url(\'assets/images/'+pic+'.svg\')"><img src="'+esc(photos[pic]||'')+'" alt="'+esc(photoAlt[pic]||'تصویر آرشیوی مرتبط با خبر')+'" title="'+esc(photoAlt[pic]||'تصویر آرشیوی')+'" loading="lazy" decoding="async" onerror="this.remove()"></div>'+
  '<div class="article-tags"><span class="tag '+(n.region==='world'?'world':'')+'">'+region+' · '+esc(n.category||'گردشگری')+'</span>'+(n.archived?'<span class="tag archive">آرشیو</span>':'')+'</div>'+
  '<h1>'+esc(n.title)+'</h1><p class="lead">'+esc(n.summary||'برای جزئیات بیشتر به منبع اصلی مراجعه کنید.')+'</p>'+
  '<div class="card-meta"><span>'+esc(dateText(n))+'</span><b>'+esc(n.source||'منبع')+'</b></div>'+
  '<div class="article-body">'+paragraphs(n.body||n.summary||'متن تکمیلی در فید منبع در دسترس نبود.')+'</div>'+
  '<aside class="article-editorial-note"><strong>زمینه و نکتهٔ تحریریه</strong><p>'+esc(context)+'</p></aside>'+
  '<div class="article-source"><b>منبع اصلی: '+esc(n.source||'منبع')+'</b><p>'+esc(dateText(n))+'</p><a class="btn btn-dark" href="'+esc(safeUrl(n.sourceUrl||n.link||'#'))+'" target="_blank" rel="noopener noreferrer">بازکردن گزارش اصلی ↗</a></div>';
}
function citySearch(){let input=$('[data-city-search]');if(!input)return;let cards=$$('[data-city]');input.addEventListener('input',()=>{let q=input.value.toLocaleLowerCase('fa');cards.forEach(c=>c.hidden=!c.innerText.toLocaleLowerCase('fa').includes(q))})}
function photoBacks(){
 const hero=$('.hero-image'),heroImg=hero&&$('img',hero);
 if(heroImg&&photos['iran-panorama']){
  heroImg.src=photos['iran-panorama'];
  heroImg.alt=photoAlt['iran-panorama'];
  heroImg.loading='eager';
  heroImg.onerror=()=>{heroImg.style.display='none'};
 }
 $$('.cover').forEach(box=>{
  if($('img',box))return;
  const match=(box.getAttribute('style')||'').match(/images\/([a-z-]+)\.svg/);
  const key=match?match[1]:'isfahan',src=photos[key]||photos.isfahan;
  if(!src)return;
  const img=document.createElement('img');
  img.src=src;img.loading='lazy';img.decoding='async';
  img.alt=photoAlt[key]||'تصویر آرشیوی؛ برای شناسایی مکان، عنوان مقصد را بررسی کنید';
  img.title=photoAlt[key]||'تصویر آرشیوی';
  img.onerror=()=>img.remove();
  box.appendChild(img);
 });
 $$('.page-art').forEach(box=>{
  const img=$('img',box);if(!img)return;
  const match=(img.getAttribute('src')||'').match(/images\/([a-z-]+)\.svg/);
  const key=match?match[1]:'isfahan';
  box.style.backgroundImage="url('assets/images/"+key+".svg')";
  box.style.backgroundSize='cover';
  img.src=photos[key]||photos['iran-panorama'];
  img.alt=photoAlt[key]||photoAlt['iran-panorama'];
  img.loading='lazy';img.decoding='async';
  img.onerror=()=>img.remove();
 });
 const detail=$('.detail-hero');
 if(detail){
  const match=(detail.getAttribute('style')||'').match(/images\/([a-z-]+)\.svg/);
  const key=match?match[1]:'isfahan';
  const img=document.createElement('img');img.className='detail-photo';
  img.src=photos[key]||photos.isfahan;
  img.alt=photoAlt[key]||'تصویر آرشیوی مرتبط با مقصد';
  img.title=photoAlt[key]||'تصویر آرشیوی';
  img.loading='lazy';img.decoding='async';img.onerror=()=>img.remove();
  detail.prepend(img);
 }
}
function menu(){let b=$('.menu-button'),n=$('#main-nav');if(!b||!n)return;b.addEventListener('click',()=>{let open=n.classList.toggle('open');b.setAttribute('aria-expanded',String(open));let s=$('span',b);if(s)s.textContent=open?'بستن':'منو'})}
async function init(){await load();latest();newsPage();destination();article();citySearch();photoBacks();menu()}init();
})();