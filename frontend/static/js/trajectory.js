if (!Auth.requireAuth()) throw 0;

const LV_META = {
  recruit:  {icon:'🛡️', name:'Recruit',  range:'0–300',    next:300},
  warden:   {icon:'🗡️', name:'Warden',   range:'301–750',   next:750},
  knight:   {icon:'⚔️', name:'Knight',   range:'751–1300',  next:1300},
  hero:     {icon:'🦅', name:'Hero',     range:'1301–1900', next:1900},
  legend:   {icon:'🔥', name:'Legend',   range:'1901–2600', next:2600},
  lord:     {icon:'👑', name:'Lord',     range:'2601–3350', next:3350},
  deity:    {icon:'🔮', name:'Deity',    range:'3351–4050', next:4050},
  titan:    {icon:'⚡', name:'Titan',    range:'4051–4500', next:4500},
};

async function initTraj() {
  Auth.fillUserUI();
  try {
    const [me, scores] = await Promise.all([api.me(), api.scores()]);
    const sp = me.student_profile || {};
    const rating   = sp.rating_score || 0;
    const academic = sp.academic_score ? Math.round(sp.academic_score * 10) / 10 : '—';
    const completed = Array.isArray(scores) ? scores.filter(s => s.is_completed).length : 0;
    const streak   = sp.current_streak || 0;
    const lvKey    = sp.level || 'recruit';
    const lv       = LV_META[lvKey] || LV_META.recruit;
    const toNext   = lv.next - rating;

    document.getElementById('stRating').textContent      = rating;
    document.getElementById('stRatingNext').textContent  = toNext > 0 ? `${toNext} ball keyingisiga` : 'Maksimal darajaga yaqin!';
    document.getElementById('stAcademic').textContent    = academic;
    document.getElementById('stTopics').textContent      = `${completed} / 45`;
    document.getElementById('stTopicsPct').textContent   = Math.round(completed / 45 * 100) + '% bajarildi';
    document.getElementById('stStreak').textContent      = `🔥 ${streak} kun streak`;
    document.getElementById('stLevel').textContent       = `${lv.icon} ${lv.name}`;
    document.getElementById('stLevelRange').textContent  = lv.range + ' oralig\'i';
    document.getElementById('stLevelNext').textContent   = toNext > 0 ? `${toNext} ball keyingisiga` : '🎉 Maksimal!';

    if (Array.isArray(scores) && scores.length) {
      const sortedScores = [...scores].sort((a,b)=>(a.topic_number||a.topic||0)-(b.topic_number||b.topic||0));
      topics.length = 0;
      sortedScores.forEach((s, i) => {
        topics.push({
          num: s.topic_number || (i+1),
          name: s.topic_title || s.topic_name || `Mavzu ${i+1}`,
          module: Math.ceil((s.topic_number || (i+1)) / 5),
          status: s.is_completed ? 'done' : (s.total_score > 0 ? 'progress' : 'locked'),
          Mo: s.mo_score||0, Ko: s.ko_score||0, Fa: s.fa_score||0,
          Ad: s.ad_score||0, Kr: s.kr_score||0, Re: s.re_score||0,
        });
      });
      renderTopicTable();
    }
  } catch(e) { console.warn('Trajectory init error:', e); }
}

const topics=[
  {num:1,name:'C# kirish va o\'rnatish',module:1,status:'done',Mo:9,Ko:18,Fa:27,Ad:13,Kr:12,Re:9},
  {num:2,name:'O\'zgaruvchilar va turlar',module:1,status:'done',Mo:8,Ko:17,Fa:25,Ad:12,Kr:11,Re:8},
  {num:3,name:'Shart operatorlari',module:1,status:'done',Mo:7,Ko:16,Fa:24,Ad:11,Kr:10,Re:7},
  {num:4,name:'Sikllar (for, while)',module:1,status:'done',Mo:8,Ko:15,Fa:22,Ad:10,Kr:9,Re:8},
  {num:5,name:'Massivlar',module:1,status:'done',Mo:7,Ko:16,Fa:23,Ad:11,Kr:11,Re:7},
  {num:6,name:'Metodlar (funksiyalar)',module:1,status:'done',Mo:8,Ko:17,Fa:24,Ad:12,Kr:10,Re:8},
  {num:7,name:'Rekursiya asoslari',module:1,status:'done',Mo:6,Ko:14,Fa:20,Ad:9,Kr:8,Re:6},
  {num:8,name:'Satrlar (string)',module:1,status:'done',Mo:7,Ko:15,Fa:22,Ad:10,Kr:9,Re:7},
  {num:9,name:'OOP: Klasslar',module:1,status:'done',Mo:8,Ko:16,Fa:25,Ad:12,Kr:11,Re:8},
  {num:10,name:'OOP: Vorislik',module:2,status:'progress',Mo:5,Ko:12,Fa:15,Ad:7,Kr:6,Re:5},
  {num:11,name:'OOP: Polimorfizm',module:2,status:'locked',Mo:0,Ko:0,Fa:0,Ad:0,Kr:0,Re:0},
  {num:12,name:'Interfeyslar',module:2,status:'locked',Mo:0,Ko:0,Fa:0,Ad:0,Kr:0,Re:0},
  {num:13,name:'Collections: List',module:2,status:'locked',Mo:0,Ko:0,Fa:0,Ad:0,Kr:0,Re:0},
  {num:14,name:'Collections: Dictionary',module:2,status:'locked',Mo:0,Ko:0,Fa:0,Ad:0,Kr:0,Re:0},
  {num:15,name:'LINQ asoslari',module:2,status:'locked',Mo:0,Ko:0,Fa:0,Ad:0,Kr:0,Re:0},
];

const modules=[
  {name:'📗 Modul 1 — C# Asoslari',done:9,total:15,pct:60,color:'#43e97b'},
  {name:'📘 Modul 2 — O\'rta daraja',done:1,total:15,pct:7,color:'#6c63ff'},
  {name:'📕 Modul 3 — Ilg\'or',done:0,total:15,pct:0,color:'#ff6584'},
];
const mpEl=document.getElementById('moduleProgress');
modules.forEach(m=>{
  mpEl.innerHTML+=`<div class="module-block">
    <div class="module-header">
      <span class="module-name">${m.name}</span>
      <span class="module-pct">${m.pct}%</span>
    </div>
    <div class="module-bar"><div class="module-bar-fill" style="width:${m.pct}%;background:${m.color}"></div></div>
    <div class="module-meta"><span>${m.done}/${m.total} mavzu</span><span>${m.done*100} ball to'plangan</span></div>
  </div>`;
});

const levels=[
  {name:'Recruit ⚔️',range:'0–300',status:'done'},
  {name:'Warden 🛡️',range:'301–750',status:'done'},
  {name:'Knight 🗡️',range:'751–1300',status:'current'},
  {name:'Hero 🦸',range:'1301–1900',status:'future'},
  {name:'Legend 🌟',range:'1901–2600',status:'future'},
  {name:'Lord 👑',range:'2601–3350',status:'future'},
];
const ltEl=document.getElementById('levelTimeline');
levels.forEach((lv,i)=>{
  ltEl.innerHTML+=`<div class="lt-item">
    <div class="lt-left">
      <div class="lt-dot ${lv.status}"></div>
      ${i<levels.length-1?'<div class="lt-line"></div>':''}
    </div>
    <div class="lt-content">
      <div class="lt-level">${lv.name}</div>
      <div class="lt-range">${lv.range} ball</div>
      <span class="lt-status ${lv.status==='done'?'st-done':lv.status==='current'?'st-curr':'st-fut'}">${lv.status==='done'?'✓ Tugallandi':lv.status==='current'?'● Hozir siz bunda':'◯ Kelajak'}</span>
    </div>
  </div>`;
});

function renderTopicTable(){
  const modF=document.getElementById('moduleFilter').value;
  const stF=document.getElementById('statusFilter').value;
  const body=document.getElementById('topicTableBody');
  body.innerHTML='';
  topics.filter(t=>{
    if(modF!=='all'&&t.module!=modF)return false;
    if(stF!=='all'&&t.status!==stF)return false;
    return true;
  }).forEach(t=>{
    const total=t.Mo+t.Ko+t.Fa+t.Ad+t.Kr+t.Re;
    const isDone=t.status==='done',isProg=t.status==='progress';
    const stBadge=isDone?'<span class="status-badge s-done">Tugatildi</span>':isProg?'<span class="status-badge s-prog">Jarayonda</span>':'<span class="status-badge s-lock">🔒 Qulflangan</span>';
    const col=isDone||isProg?'':'style="opacity:.35"';
    body.innerHTML+=`<tr ${col}>
      <td class="topic-name-cell"><span class="topic-num">${t.num}</span>${t.name}</td>
      <td class="criterion-cell c-mo">${t.Mo||'—'}</td>
      <td class="criterion-cell c-ko">${t.Ko||'—'}</td>
      <td class="criterion-cell c-fa">${t.Fa||'—'}</td>
      <td class="criterion-cell c-ad">${t.Ad||'—'}</td>
      <td class="criterion-cell c-kr">${t.Kr||'—'}</td>
      <td class="criterion-cell c-re">${t.Re||'—'}</td>
      <td class="total-cell" style="color:${total>=80?'#43e97b':total>=60?'#ffd700':total>0?'#ff6584':'var(--muted)'}">${total||'—'}</td>
      <td>${stBadge}</td>
    </tr>`;
  });
}
renderTopicTable();

const critData=[
  {name:'Motivatsion (Mo)',max:10,avg:7.2,color:'#60a5fa',trend:'↑+0.8'},
  {name:'Kognitiv (Ko)',max:20,avg:15.8,color:'#a78bfa',trend:'↑+1.2'},
  {name:'Faoliyat (Fa)',max:30,avg:23.4,color:'#43e97b',trend:'↑+2.1'},
  {name:'Adaptiv (Ad)',max:15,avg:11.2,color:'#ffd700',trend:'↑+0.5'},
  {name:'Kreativ (Kr)',max:15,avg:10.8,color:'#ff6584',trend:'↓-0.3'},
  {name:'Reflektiv (Re)',max:10,avg:6.9,color:'#fb923c',trend:'↑+0.4'},
];
const csBody=document.getElementById('critStatsBody');
critData.forEach(c=>{
  const pct=Math.round(c.avg/c.max*100);
  csBody.innerHTML+=`<tr>
    <td style="font-weight:600;color:${c.color}">${c.name}</td>
    <td style="font-weight:700">${c.avg}/${c.max}</td>
    <td><div class="bar-inline"><div class="bi-bar"><div class="bi-fill" style="width:${pct}%;background:${c.color}"></div></div><span class="bi-val" style="color:${c.color}">${pct}%</span></div></td>
    <td style="font-size:.78rem;font-weight:600;color:${c.trend.startsWith('↑')?'#43e97b':'#ff6584'}">${c.trend}</td>
  </tr>`;
});

const waEl=document.getElementById('weakAreas');
[
  {icon:'💡',title:'Kreativ baholash past (10.8/15)',text:'Kreativ (Kr) mezoni bo\'yicha o\'rtacha ball past. Muammoga noodatiy yechim topish va original kod yozish ko\'nikmalarini rivojlantirish kerak.',color:'rgba(255,101,132,0.06)'},
  {icon:'📝',title:'Reflektiv ball rivojlanish yo\'lida (6.9/10)',text:'Mavzu bo\'yicha journal yozish va o\'z-o\'zini tahlil qilish sifatini oshirish kerak. Har bir mavzudan so\'ng chuqur fikr yozing.',color:'rgba(251,146,60,0.06)'},
].forEach(w=>{
  waEl.innerHTML+=`<div class="ai-insight" style="background:${w.color}">
    <span class="ai-icon">${w.icon}</span>
    <div class="ai-text"><strong>${w.title}</strong><br>${w.text}</div>
  </div>`;
});

const saEl=document.getElementById('strongAreas');
[
  {icon:'💪',title:'Faoliyat mezoni yuqori (23.4/30 = 78%)',text:'Kod yozish va amaliyot topshiriqlarni bajarishda kuchli ko\'rsatkichlar. Bu siz uchun asosiy ustunlik.'},
  {icon:'🧠',title:'Kognitiv o\'sish yaxshi (15.8/20 = 79%)',text:'Nazariy bilimlarni o\'zlashtirish sur\'ati jadal. Murakkab mavzularni ham tez tushunasiz.'},
].forEach(s=>{
  saEl.innerHTML+=`<div class="ai-insight" style="background:rgba(67,233,123,0.05);border-color:rgba(67,233,123,0.15)">
    <span class="ai-icon">${s.icon}</span>
    <div class="ai-text"><strong>${s.title}</strong><br>${s.text}</div>
  </div>`;
});

const aiEl=document.getElementById('aiInsights');
[
  {icon:'🎯',text:'<strong>Asosiy tavsiya:</strong> Haftasiga 3 mavzudan ko\'proq o\'tish sur\'atini saqlang. Hozirgi sur\'atda semestr oxirida Hero darajasiga erishish mumkin.'},
  {icon:'⚡',text:'<strong>Duel strategiyasi:</strong> Ko\'proq duel o\'tkazish (haftasiga 5+) Rating Scoreni tezroq oshiradi. Algoritm masalalariga e\'tibor bering.'},
  {icon:'💡',text:'<strong>Kreativ mezon uchun:</strong> Har bir mavzuda kamida bitta original yechim (standartdan farqli) taqdim eting.'},
  {icon:'📈',text:'<strong>Prognoz to\'g\'risida:</strong> Joriy sur\'atingizni 15% oshirsangiz, Legend darajasiga (1901+) erishish realistik.'},
].forEach(a=>{
  aiEl.innerHTML+=`<div class="ai-insight"><span class="ai-icon">${a.icon}</span><div class="ai-text">${a.text}</div></div>`;
});

const months=['Sen','Okt','Noy','Dek','Yan','Fev','Mar','Apr','May','Iyu','Iyu','Avg'];
const hmL=document.getElementById('hmLabels');
months.forEach(m=>hmL.innerHTML+=`<div class="hm-label">${m}</div>`);
const hmG=document.getElementById('heatmapGrid');
const hmVals=[0,1,2,3,4,3,2,1,2,3,4,3,2,3,4,3,2,1,0,1,2,3,2,1,0,0,1,2,3,2,1,2,3,4,3,2,1,2,3,4,3,2,1,0,1,2,3,4,3,2,1,2,3,4,3,2,1,2,3,4,3,2,1,0,1,2,3,4,3,2,1,2,3,4,3,2,1,2,3,4,3,2,1,0,1,2,3,4,3,2,1,2,3,4,3,2,1,2,3,4,3,2,1,0,1,2,3,4,3,2,1,2,3,4,3,2,1,2,3,4,3,2,1,0,1,2,3,4,3,2,1,2,3,4,3,2,1,2,3,4,3,2,1,0];
hmVals.slice(0,144).forEach((v,i)=>{
  hmG.innerHTML+=`<div class="hm-cell hm-${v}" title="Kun ${i+1}: ${v} ta mavzu"></div>`;
});

(function(){
  const c=document.getElementById('trajectoryChart');
  if(!c)return;
  const ctx=c.getContext('2d');
  c.width=c.offsetWidth*devicePixelRatio;c.height=c.offsetHeight*devicePixelRatio;
  ctx.scale(devicePixelRatio,devicePixelRatio);
  const W=c.offsetWidth/devicePixelRatio,H=c.offsetHeight/devicePixelRatio;
  const actualData=[100,180,260,320,400,480,540,620,710,842];
  const forecastData=[null,null,null,null,null,null,null,null,null,842,960,1080,1200,1350,1480,1620];
  const labels=['W1','W2','W3','W4','W5','W6','W7','W8','W9','W10','W11','W12','W13','W14','W15','W16'];
  const pad={l:50,r:20,t:20,b:30};
  const iW=W-pad.l-pad.r,iH=H-pad.t-pad.b;
  const max=1800,min=0;
  const lvls=[{y:300,lbl:'Warden',c:'rgba(100,200,100,0.25)'},{y:750,lbl:'Knight',c:'rgba(100,150,255,0.25)'},{y:1300,lbl:'Hero',c:'rgba(255,200,100,0.25)'}];
  lvls.forEach(lv=>{
    const yp=pad.t+iH*(1-(lv.y-min)/(max-min));
    ctx.strokeStyle=lv.c;ctx.lineWidth=1;ctx.setLineDash([5,5]);
    ctx.beginPath();ctx.moveTo(pad.l,yp);ctx.lineTo(pad.l+iW,yp);ctx.stroke();
    ctx.fillStyle=lv.c.replace('0.25','0.8');ctx.font='10px Segoe UI';ctx.textAlign='left';
    ctx.fillText(lv.lbl,pad.l+4,yp-4);
  });
  ctx.setLineDash([]);
  ctx.strokeStyle='rgba(255,255,255,0.05)';ctx.lineWidth=1;
  for(let i=0;i<=5;i++){
    const y=pad.t+iH*i/5;const v=Math.round(max*(1-i/5));
    ctx.beginPath();ctx.moveTo(pad.l,y);ctx.lineTo(pad.l+iW,y);ctx.stroke();
    ctx.fillStyle='rgba(136,146,176,0.7)';ctx.font='10px Segoe UI';ctx.textAlign='right';
    ctx.fillText(v,pad.l-6,y+4);
  }
  const pts=actualData.map((v,i)=>({x:pad.l+iW*i/(labels.length-1),y:pad.t+iH*(1-(v-min)/(max-min))}));
  const grad=ctx.createLinearGradient(0,pad.t,0,pad.t+iH);
  grad.addColorStop(0,'rgba(108,99,255,0.35)');grad.addColorStop(1,'rgba(108,99,255,0)');
  ctx.beginPath();ctx.moveTo(pts[0].x,pad.t+iH);
  pts.forEach(p=>ctx.lineTo(p.x,p.y));ctx.lineTo(pts[pts.length-1].x,pad.t+iH);ctx.closePath();
  ctx.fillStyle=grad;ctx.fill();
  ctx.beginPath();ctx.strokeStyle='#6c63ff';ctx.lineWidth=2.5;ctx.setLineDash([]);
  pts.forEach((p,i)=>i===0?ctx.moveTo(p.x,p.y):ctx.lineTo(p.x,p.y));ctx.stroke();
  pts.forEach(p=>{ctx.beginPath();ctx.arc(p.x,p.y,3.5,0,Math.PI*2);ctx.fillStyle='#6c63ff';ctx.fill();});
  const fcStart=actualData.length-1;
  const fcPts=forecastData.slice(fcStart).map((v,i)=>({x:pad.l+iW*(fcStart+i)/(labels.length-1),y:pad.t+iH*(1-(v-min)/(max-min))}));
  ctx.beginPath();ctx.strokeStyle='rgba(167,139,250,0.6)';ctx.lineWidth=2;ctx.setLineDash([8,5]);
  fcPts.forEach((p,i)=>i===0?ctx.moveTo(p.x,p.y):ctx.lineTo(p.x,p.y));ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle='rgba(136,146,176,0.7)';ctx.font='10px Segoe UI';ctx.textAlign='center';
  labels.forEach((l,i)=>{if(i%2===0)ctx.fillText(l,pad.l+iW*i/(labels.length-1),H-6);});
})();

(function(){
  const c=document.getElementById('radarChart');
  if(!c)return;
  const ctx=c.getContext('2d');
  c.width=200;c.height=200;
  const cx=100,cy=100,r=75;
  const labels=['Mo','Ko','Fa','Ad','Kr','Re'];
  const values=[72,79,78,75,72,69];
  const colors=['#60a5fa','#a78bfa','#43e97b','#ffd700','#ff6584','#fb923c'];
  const n=labels.length;
  const ang=Array.from({length:n},(_,i)=>-Math.PI/2+2*Math.PI*i/n);
  for(let g=1;g<=4;g++){
    ctx.beginPath();ctx.strokeStyle='rgba(255,255,255,0.06)';ctx.lineWidth=1;
    ang.forEach((a,i)=>{const x=cx+r*(g/4)*Math.cos(a),y=cy+r*(g/4)*Math.sin(a);i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);});
    ctx.closePath();ctx.stroke();
  }
  ang.forEach(a=>{ctx.beginPath();ctx.strokeStyle='rgba(255,255,255,0.08)';ctx.lineWidth=1;ctx.moveTo(cx,cy);ctx.lineTo(cx+r*Math.cos(a),cy+r*Math.sin(a));ctx.stroke();});
  ctx.beginPath();ctx.fillStyle='rgba(108,99,255,0.15)';ctx.strokeStyle='rgba(108,99,255,0.8)';ctx.lineWidth=2;
  values.forEach((v,i)=>{const x=cx+r*(v/100)*Math.cos(ang[i]),y=cy+r*(v/100)*Math.sin(ang[i]);i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);});
  ctx.closePath();ctx.fill();ctx.stroke();
  values.forEach((v,i)=>{
    const x=cx+r*(v/100)*Math.cos(ang[i]),y=cy+r*(v/100)*Math.sin(ang[i]);
    ctx.beginPath();ctx.arc(x,y,3.5,0,Math.PI*2);ctx.fillStyle=colors[i];ctx.fill();
    const lx=cx+(r+16)*Math.cos(ang[i]),ly=cy+(r+16)*Math.sin(ang[i]);
    ctx.fillStyle=colors[i];ctx.font='bold 9.5px Segoe UI';ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.fillText(labels[i],lx,ly);
  });
})();

(function(){
  const c=document.getElementById('criteriaChart');
  if(!c)return;
  const ctx=c.getContext('2d');
  c.width=c.offsetWidth*devicePixelRatio;c.height=c.offsetHeight*devicePixelRatio;
  ctx.scale(devicePixelRatio,devicePixelRatio);
  const W=c.offsetWidth/devicePixelRatio,H=c.offsetHeight/devicePixelRatio;
  const labels=['Mo','Ko','Fa','Ad','Kr','Re'];
  const maxVals=[10,20,30,15,15,10];
  const avgVals=[7.2,15.8,23.4,11.2,10.8,6.9];
  const colors=['#60a5fa','#a78bfa','#43e97b','#ffd700','#ff6584','#fb923c'];
  const pad={l:20,r:10,t:15,b:25};
  const iW=W-pad.l-pad.r,iH=H-pad.t-pad.b;
  const bW=iW/labels.length*0.55,gap=iW/labels.length;
  labels.forEach((lbl,i)=>{
    const x=pad.l+gap*i+(gap-bW)/2;
    const maxH=iH;const avgH=iH*(avgVals[i]/maxVals[i]);
    ctx.fillStyle=colors[i]+'33';
    ctx.beginPath();ctx.roundRect(x,pad.t,bW,maxH,3);ctx.fill();
    ctx.fillStyle=colors[i];
    ctx.beginPath();ctx.roundRect(x,pad.t+maxH-avgH,bW,avgH,3);ctx.fill();
    ctx.fillStyle='rgba(136,146,176,0.8)';ctx.font='bold 11px Segoe UI';ctx.textAlign='center';
    ctx.fillText(lbl,x+bW/2,H-5);
    ctx.fillStyle=colors[i];ctx.font='bold 10px Segoe UI';
    ctx.fillText(avgVals[i],x+bW/2,pad.t+maxH-avgH-5);
  });
})();

(function(){
  const c=document.getElementById('weeklyChart');
  if(!c)return;
  const ctx=c.getContext('2d');
  c.width=c.offsetWidth*devicePixelRatio;c.height=c.offsetHeight*devicePixelRatio;
  ctx.scale(devicePixelRatio,devicePixelRatio);
  const W=c.offsetWidth/devicePixelRatio,H=c.offsetHeight/devicePixelRatio;
  const data=[1.5,2.0,3.5,2.8,1.2,4.2,3.0];
  const days=['Du','Se','Ch','Pa','Ju','Sh','Ya'];
  const pad={l:25,r:10,t:10,b:25};
  const iW=W-pad.l-pad.r,iH=H-pad.t-pad.b;
  const max=5,bW=iW/data.length*0.5;
  data.forEach((v,i)=>{
    const x=pad.l+(iW/(data.length))*(i+0.25);
    const bH=iH*(v/max);
    const grad=ctx.createLinearGradient(0,pad.t+iH-bH,0,pad.t+iH);
    grad.addColorStop(0,'#6c63ff');grad.addColorStop(1,'rgba(108,99,255,0.2)');
    ctx.fillStyle=grad;
    ctx.beginPath();ctx.roundRect(x,pad.t+iH-bH,bW,bH,3);ctx.fill();
    ctx.fillStyle='rgba(136,146,176,0.8)';ctx.font='10px Segoe UI';ctx.textAlign='center';
    ctx.fillText(days[i],x+bW/2,H-5);
  });
})();

(function(){
  const c=document.getElementById('forecastChart');
  if(!c)return;
  const ctx=c.getContext('2d');
  c.width=c.offsetWidth*devicePixelRatio;c.height=c.offsetHeight*devicePixelRatio;
  ctx.scale(devicePixelRatio,devicePixelRatio);
  const W=c.offsetWidth/devicePixelRatio,H=c.offsetHeight/devicePixelRatio;
  const optimistic=[842,920,1020,1120,1250,1380,1520,1680,1850,2050];
  const realistic=[842,900,960,1020,1100,1180,1260,1350,1420,1500];
  const pessimistic=[842,870,900,930,960,1000,1050,1100,1150,1200];
  const labels=['W10','W11','W12','W13','W14','W15','W16','W17','W18','W19'];
  const pad={l:50,r:20,t:20,b:30};
  const iW=W-pad.l-pad.r,iH=H-pad.t-pad.b;
  const max=2200,min=600;
  const drawLine=(data,color,dash=[])=>{
    const pts=data.map((v,i)=>({x:pad.l+iW*i/(data.length-1),y:pad.t+iH*(1-(v-min)/(max-min))}));
    ctx.beginPath();ctx.strokeStyle=color;ctx.lineWidth=2;ctx.setLineDash(dash);
    pts.forEach((p,i)=>i===0?ctx.moveTo(p.x,p.y):ctx.lineTo(p.x,p.y));ctx.stroke();
    ctx.setLineDash([]);
  };
  ctx.strokeStyle='rgba(255,255,255,0.05)';ctx.lineWidth=1;
  for(let i=0;i<=5;i++){
    const y=pad.t+iH*i/5;
    ctx.beginPath();ctx.moveTo(pad.l,y);ctx.lineTo(pad.l+iW,y);ctx.stroke();
    ctx.fillStyle='rgba(136,146,176,0.7)';ctx.font='10px Segoe UI';ctx.textAlign='right';
    ctx.fillText(Math.round(max*(1-i/5)+min*i/5),pad.l-5,y+4);
  }
  drawLine(pessimistic,'rgba(255,101,132,0.7)',[6,4]);
  drawLine(realistic,'rgba(167,139,250,0.9)',[]);
  drawLine(optimistic,'rgba(67,233,123,0.8)',[4,3]);
  ctx.fillStyle='rgba(136,146,176,0.7)';ctx.font='10px Segoe UI';ctx.textAlign='center';
  labels.forEach((l,i)=>{if(i%2===0)ctx.fillText(l,pad.l+iW*i/(labels.length-1),H-5);});
})();

function switchTab(id){
  const ids=['overview','topics','criteria','activity','forecast'];
  document.querySelectorAll('.tab-btn').forEach((b,i)=>b.classList.toggle('active',ids[i]===id));
  document.querySelectorAll('.tab-content').forEach(t=>t.classList.toggle('active',t.id==='tab-'+id));
}

initTraj();
