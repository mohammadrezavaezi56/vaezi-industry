(()=>{
'use strict';
const $=(s,r=document)=>r.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const norm=s=>String(s||'').toLocaleLowerCase('fa').replace(/ي/g,'ی').replace(/ك/g,'ک');
const imageMap={isfahan:'isfahan.jpg',rasht:'rasht.jpg',yazd:'yazd.jpg',shiraz:'shiraz.jpg',kish:'kish.jpg',qeshm:'qeshm.jpg',tehran:'tehran.jpg',persepolis:'persepolis.jpg',desert:'desert.jpg',guesthouse:'guesthouse.jpg','iran-panorama':'iran-panorama.jpg',world:'guesthouse.jpg'};
function hash(v){let h=2166136261;for(const c of String(v||'')){h^=c.charCodeAt(0);h=Math.imul(h,16777619)}return h>>>0}
function imageFor(n){
 const t=norm([n.title,n.summary,n.body,n.context,n.category].join(' ')),h=hash(n.id+'|'+n.title);
 const rules=[[/دریا|ساحل|جزیره|کیش|قشم|بندر|خلیج|کشتی|کروز/,['kish','qeshm']],[/جنگل|طبیعت|گیلان|مازندران|ماسوله|روستا|آبشار|محیط.?زیست/,['rasht','guesthouse','desert']],[/تهران|میلاد|فرودگاه|نمایشگاه|همایش/,['tehran','iran-panorama']],[/یزد|بادگیر|کویر|کلوت|بیابان/,['yazd','desert']],[/اصفهان|نقش.?جهان|تخت.?جمشید|میراث|تاریخی|فرهنگ|مسجد|موزه/,['isfahan','shiraz','persepolis','yazd']]];
 for(const [re,choices] of rules)if(re.test(t))return choices[h%choices.length];
 const fallback=n.region==='world'?['iran-panorama','tehran','kish','rasht','yazd','shiraz','desert']:['isfahan','rasht','tehran','kish','yazd','shiraz','guesthouse','desert','qeshm','persepolis'];
 return fallback[h%fallback.length];
}
function dateText(n){if(n.displayDate)return n.displayDate;if(!n.publishedAt)return 'تاریخ در منبع مشخص نشده';const d=new Date(n.publishedAt);return Number.isNaN(d.getTime())?String(n.publishedAt):new Intl.DateTimeFormat('fa-IR',{dateStyle:'medium'}).format(d)}
function short(s,max=180){s=String(s||'').trim();return s.length>max?s.slice(0,max-1).trimEnd()+'…':s}
function safeUrl(s){try{const u=new URL(s,location.href);return ['https:','http:'].includes(u.protocol)?u.href:'#'}catch{return '#'}}
function card(n){
 const img=imageFor(n),imgPath='assets/images/photos/'+(imageMap[img]||imageMap['iran-panorama']);
 return '<article class="news-card tourism-news-card"><div class="cover"><img loading="lazy" decoding="async" src="'+imgPath+'" alt="'+esc('تصویر سفر مرتبط با '+(n.category||'گردشگری'))+'"></div><div class="card-body"><span class="tag '+(n.region==='world'?'world':'')+'">'+esc(n.region==='world'?'جهان':'ایران')+' · '+esc(n.category||'اخبار گردشگری')+'</span><h3><a href="article.html?id='+encodeURIComponent(n.id)+'">'+esc(n.title)+'</a></h3><p class="card-summary">'+esc(short(n.summary||n.body||'برای جزئیات بیشتر، منبع اصلی را ببینید.'))+'</p><div class="card-meta"><span>'+esc(dateText(n))+'</span><b>'+esc(n.source||'منبع اصلی')+'</b></div><div class="card-actions"><a class="mini-btn" href="article.html?id='+encodeURIComponent(n.id)+'">متن کامل ←</a><a class="text-link" href="'+esc(safeUrl(n.sourceUrl||n.link||'#'))+'" target="_blank" rel="noopener noreferrer">منبع اصلی ↗</a></div></div></article>';
}
function sortLatest(a,b){return String(b.publishedAt||'').localeCompare(String(a.publishedAt||''))}
function choose(items,re,count,used){
 const matches=items.filter(n=>n.region!=='world'&&re.test(norm([n.title,n.summary,n.body,n.category,n.source].join(' ')))&&!used.has(n.id)).sort(sortLatest),out=[];
 for(const n of matches){if(out.length>=count)break;out.push(n);used.add(n.id)}
 return out;
}
async function init(){
 const grids={industry:$('[data-tourism-grid="industry"]'),booking:$('[data-tourism-grid="booking"]')},status=$('[data-tourism-status]');
 try{
  const res=await fetch('news.json?refresh=1',{cache:'no-store',headers:{'Accept':'application/json'}});
  if(!res.ok)throw new Error('News archive unavailable: '+res.status);
  const payload=await res.json(),items=(Array.isArray(payload)?payload:payload.items||[]).filter(n=>n&&n.id&&n.title&&String(n.sourceUrl||n.link||'').startsWith('http')).sort(sortLatest);
  if(!items.length)throw new Error('Empty archive');
  const used=new Set(),booking=choose(items,/(اقامت|هتل|رزرو|میزبان|پلتفرم|جاباما|میهمان.?شو|جاجیگا|اتاقک|اجاره.?کوتاه|پرداخت|لغو|کمیسیون|اقامت و هتلداری)/,4,used);
  if(booking.length<4){for(const n of items){if(booking.length>=4)break;if(n.region!=='world'&&!used.has(n.id)){booking.push(n);used.add(n.id)}}}
  const industry=choose(items,/(سرمایه.?گذاری|تسهیلات|صنعت گردشگری|سیاست.?گذاری|حمل.?ونقل|گردشگری سلامت|گردشگری پایدار|میراث|صنایع.?دستی|اشتغال|آژانس|رویداد|گردشگری|مسافرت|هتلداری)/,4,used);
  if(industry.length<4){for(const n of items){if(industry.length>=4)break;if(!used.has(n.id)){industry.push(n);used.add(n.id)}}}
  if(grids.industry)grids.industry.innerHTML=industry.map(card).join('')||'<p>خبر مرتبطی برای این بخش پیدا نشد.</p>';
  if(grids.booking)grids.booking.innerHTML=booking.map(card).join('')||'<p>خبر مرتبطی برای این بخش پیدا نشد.</p>';
  const count=$('[data-tourism-count]');if(count)count.textContent=new Intl.NumberFormat('fa-IR').format(items.length)+' مطلب';
  if(status){let when='زمان به‌روزرسانی نامشخص';if(payload.updatedAt){const d=new Date(payload.updatedAt);if(!Number.isNaN(d.getTime()))when=new Intl.DateTimeFormat('fa-IR',{dateStyle:'medium',timeStyle:'short'}).format(d)}status.textContent='آرشیو بررسی شد: '+new Intl.NumberFormat('fa-IR').format(items.length)+' مطلب · آخرین بازبینی: '+when+'؛ برای اطلاعات کامل‌تر، لینک منبع هر خبر را دنبال کنید.'}
 }catch(err){
  Object.values(grids).filter(Boolean).forEach(g=>g.innerHTML='<p class="tourism-fallback">اتصال به آرشیو در دسترس نیست. <a href="news.html">ورود به صفحهٔ اخبار</a></p>');
  if(status)status.textContent='آرشیو تازه در دسترس نبود؛ برای دیدن خبرها صفحهٔ اخبار را باز کنید.';
  console.warn('Tourism page archive load failed',err);
 }
}
init();
})();