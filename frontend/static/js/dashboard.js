if (!Auth.requireAuth()) throw 0;

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('overlay').classList.toggle('show');
}
function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('overlay').classList.remove('show');
}

const LEVEL_META = {
  recruit: {icon:'🗡️', range:'0–300'},   warden: {icon:'🛡️', range:'301–750'},
  knight:  {icon:'⚔️', range:'751–1300'}, hero:   {icon:'🦸', range:'1301–1900'},
  legend:  {icon:'🌟', range:'1901–2600'}, lord:   {icon:'👑', range:'2601–3350'},
  deity:   {icon:'✨', range:'3351–4050'}, titan:  {icon:'🏔️', range:'4051–4500'},
};
const CHAR_DATA = {
  warrior:    {avatar:'⚔️', name:'Jangchi',      en:'Warrior',    weapons:['⚔️ Qilich','🏹 Nayza','🛡️ Zirh']},
  ranger:     {avatar:'🏹', name:'Sarguzashtchi', en:'Ranger',     weapons:['🏹 Nayza','👟 Etik','🥋 Engil Zirh']},
  sorceress:  {avatar:'🔮', name:'Sehrgar Ayol',  en:'Sorceress',  weapons:['🪄 Tayoqcha','💍 Uzuk']},
  knight:     {avatar:'🛡️', name:'Ritsar',        en:'Knight',     weapons:['⚔️ Qilich','🛡️ Qalqon','🏰 Zirh']},
  ladyknight: {avatar:'⚜️', name:'Ayol Ritsar',   en:'Lady Knight',weapons:['⚔️ Qilich','🛡️ Qalqon','🏰 Zirh','💍 Uzuk']},
};
const SCORE_COLOR = s => s>=85?'#43e97b':s>=70?'#4299e1':s>=60?'#ffa500':'#ff6584';
const BAR_GRAD    = s => s>=85?'linear-gradient(90deg,#43e97b,#38f9d7)':s>=70?'linear-gradient(90deg,#4299e1,#63b3ed)':'linear-gradient(90deg,#ffa500,#ffd700)';

async function loadDashboard() {
  Auth.fillUserUI();
  try {
    const [user, scores, badges, notifs] = await Promise.all([
      api.me(),
      api.scores(),
      api.myBadges().catch(() => []),
      api.notifications().catch(() => []),
    ]);
    Auth.setUser(user);
    const sp = user.student_profile || {};
    const rating  = sp.rating_score  || 0;
    const streak  = sp.current_streak || 0;
    const maxStr  = sp.max_streak     || 0;
    const lvl     = sp.level || 'recruit';
    const lvlPct  = sp.level_pct || 0;
    const lm      = LEVEL_META[lvl] || LEVEL_META.recruit;
    const name = user.full_name || user.username || 'Talaba';
    const active = scores.find(s => !s.is_completed && s.total_score > 0);
    const greetSub = active ? `· "${active.topic_title || 'Mavzu'}" davom etmoqda` : '';
    setText('topbarGreet', `Xush kelibsiz, ${name}! ${greetSub}`);
    const unread = Array.isArray(notifs) ? notifs.filter(n => !n.is_read).length : 0;
    if (unread > 0) {
      const dot   = document.getElementById('notifDot');
      const badge = document.getElementById('notifBadge');
      if (dot)   dot.style.display   = '';
      if (badge) { badge.style.display = ''; badge.textContent = unread > 9 ? '9+' : unread; }
    }
    const completed = scores.filter(s => s.is_completed).length;
    const avgScore  = scores.length ? Math.round(scores.reduce((a,s) => a + s.total_score, 0) / scores.length) : 0;
    setText('statRating',   rating);
    setText('statAcademic', avgScore);
    setText('statTopics',   completed);
    setText('statStreak',   streak);
    setText('statMaxStreak', 'Rekord: ' + maxStr + ' kun');
    const LEVEL_NAMES = {
      recruit:'Yangi Askar', warden:'Navbatchi', knight:'Ritsar',
      hero:'Qahramon', legend:'Afsona', lord:'Lord', deity:'Iloh', titan:'Titan',
    };
    setText('levelName',  LEVEL_NAMES[lvl] || lvl);
    setText('levelRange',  lm.range + ' Rating Score');
    setText('levelIcon',   lm.icon);
    document.getElementById('xpFill').style.width = lvlPct + '%';
    setText('xpCurrent', rating + ' ball');
    const hiStr = lm.range.split('–')[1] || '300';
    const loBound = parseInt(hiStr.replace(/\D/g,'')) || 300;
    setText('xpLeft', loBound - rating > 0 ? (loBound - rating) + ' qoldi' : 'Maksimal!');
    renderTopics(scores);
    const avgMo = avgField(scores,'mo_score');
    const avgKo = avgField(scores,'ko_score');
    const avgFa = avgField(scores,'fa_score');
    const avgAd = avgField(scores,'ad_score');
    const avgKr = avgField(scores,'kr_score');
    const avgRe = avgField(scores,'re_score');
    drawRadar([avgMo, avgKo, avgFa, avgAd, avgKr, avgRe]);
    drawLine(scores);
    renderCharacter(sp.character);
    renderBadges(badges);
    drawStreak(streak);
  } catch (err) {
    console.error('Dashboard yuklanmadi:', err);
  }
}

function renderCharacter(charId) {
  const c = CHAR_DATA[charId] || CHAR_DATA.warrior;
  const wrap = document.getElementById('charDisplay');
  if (!wrap) return;
  document.getElementById('charAva').textContent   = c.avatar;
  document.getElementById('charName').textContent  = c.name;
  document.getElementById('charEn').textContent    = c.en;
  document.getElementById('charWeapons').innerHTML = c.weapons.map(w => `<span class="w-chip">${w}</span>`).join('');
  wrap.style.display = 'block';
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function avgField(scores, field) {
  if (!scores.length) return 0;
  return scores.reduce((a, s) => a + (s[field] || 0), 0) / scores.length;
}

function renderTopics(scores) {
  const list = document.getElementById('topicList');
  if (!list) return;
  if (!scores.length) {
    list.innerHTML = '<div style="color:var(--muted);padding:1rem;text-align:center">Hali mavzu boshlalmagan</div>';
    return;
  }
  const sorted = [...scores].sort((a, b) => {
    const pa = !a.is_completed && a.total_score > 0 ? 0 : a.is_completed ? 2 : 1;
    const pb = !b.is_completed && b.total_score > 0 ? 0 : b.is_completed ? 2 : 1;
    return pa - pb || (a.topic_number || 0) - (b.topic_number || 0);
  });
  const show = sorted.slice(0, 10);
  list.innerHTML = show.map(t => {
    const pct   = t.total_score || 0;
    const done  = t.is_completed;
    const actv  = !done && pct > 0;
    const st    = done ? 'completed' : actv ? 'inprogress' : 'available';
    const label = done ? 'Yakunlandi' : actv ? 'Jarayonda' : 'Ochiq';
    const num   = t.topic_number || t.topic;
    const title = t.topic_title  || `Mavzu ${num}`;
    return `<div class="topic-item" onclick="window.location.href='/mainquest.html'">
      <div class="t-num">${num}</div>
      <div class="t-info">
        <div class="t-name">${title}</div>
        <div class="t-bar-wrap">
          <div class="t-bar"><div class="t-bar-fill" style="width:${pct}%;background:${pct?BAR_GRAD(pct):'rgba(255,255,255,0.1)'}"></div></div>
          <div class="t-pct">${pct ? pct + '/100' : ''}</div>
        </div>
      </div>
      ${pct ? `<div class="t-score" style="color:${SCORE_COLOR(pct)}">${pct}</div>` : ''}
      <div class="t-status s-${st}">${label}</div>
    </div>`;
  }).join('');
}

function renderBadges(badges) {
  const wrap = document.querySelector('.badges-grid');
  if (!wrap || !badges.length) return;
  wrap.innerHTML = badges.map(b => `
    <div class="badge-chip">
      <div class="bi">${b.badge?.icon || '🏅'}</div>
      <div class="bn">${b.badge?.name || 'Badge'}</div>
    </div>`).join('');
}

function drawStreak(streak) {
  const row = document.getElementById('streakRow');
  if (!row) return;
  row.innerHTML = Array.from({length:30}, (_,i) => {
    const day = 30 - i;
    const cls = day === 1 ? 'dd-today' : day <= streak ? 'dd-active' : 'dd-empty';
    return `<div class="day-dot ${cls}" title="${day}-kun avval">${day}</div>`;
  }).reverse().join('');
}

function drawLine(scores) {
  const canvas = document.getElementById('lineChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  function resize() { canvas.width = canvas.offsetWidth; canvas.height = canvas.offsetHeight; }
  resize();
  window.addEventListener('resize', () => { resize(); draw(); });
  const data   = scores.slice(-10).map(s => s.total_score || 0);
  const labels = scores.slice(-10).map((_,i) => 'M'+(i+1));
  function draw() {
    if (!data.length) return;
    const W=canvas.width, H=canvas.height;
    ctx.clearRect(0,0,W,H);
    const pad = {t:20,r:20,b:30,l:35};
    const gw=W-pad.l-pad.r, gh=H-pad.t-pad.b;
    const min=0, max=100;
    const xs = data.map((_,i) => pad.l+(data.length>1?i/(data.length-1):0.5)*gw);
    const ys = data.map(s => pad.t+gh-(s-min)/(max-min)*gh);
    [25,50,75,100].forEach(v => {
      const y = pad.t+gh-(v-min)/(max-min)*gh;
      ctx.beginPath(); ctx.moveTo(pad.l,y); ctx.lineTo(W-pad.r,y);
      ctx.strokeStyle = 'rgba(255,255,255,0.05)'; ctx.lineWidth = 1; ctx.stroke();
      ctx.fillStyle = 'rgba(136,146,176,0.6)'; ctx.font = '10px Segoe UI'; ctx.textAlign = 'right';
      ctx.fillText(v, pad.l-5, y+4);
    });
    const grad = ctx.createLinearGradient(0,pad.t,0,H-pad.b);
    grad.addColorStop(0,'rgba(108,99,255,0.25)'); grad.addColorStop(1,'rgba(108,99,255,0)');
    ctx.beginPath(); ctx.moveTo(xs[0],ys[0]);
    xs.forEach((_,i) => { if(i>0) ctx.lineTo(xs[i],ys[i]); });
    ctx.lineTo(xs[xs.length-1],H-pad.b); ctx.lineTo(xs[0],H-pad.b); ctx.closePath();
    ctx.fillStyle = grad; ctx.fill();
    ctx.beginPath(); ctx.moveTo(xs[0],ys[0]);
    xs.forEach((_,i) => { if(i>0) ctx.lineTo(xs[i],ys[i]); });
    ctx.strokeStyle = '#6c63ff'; ctx.lineWidth = 2.5; ctx.lineJoin = 'round'; ctx.stroke();
    xs.forEach((x,i) => {
      ctx.beginPath(); ctx.arc(x,ys[i],5,0,Math.PI*2); ctx.fillStyle = '#6c63ff'; ctx.fill();
      ctx.beginPath(); ctx.arc(x,ys[i],3,0,Math.PI*2); ctx.fillStyle = '#fff'; ctx.fill();
      ctx.fillStyle = 'rgba(136,146,176,0.7)'; ctx.font = '10px Segoe UI'; ctx.textAlign = 'center';
      ctx.fillText(labels[i], x, H-pad.b+14);
    });
  }
  draw();
}

function drawRadar(values) {
  const canvas = document.getElementById('radarChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W=canvas.width, H=canvas.height;
  const cx=W/2, cy=H/2, r=Math.min(W,H)/2-30;
  const labels = ['Motivatsion','Kognitiv','Faoliyatli','Adaptiv','Kreativlik','Refleksiv'];
  const maxVals = [10,20,30,15,15,10];
  const n = labels.length;
  const getXY = (i, frac) => {
    const a = (-Math.PI/2)+(i/n)*2*Math.PI;
    return {x: cx+Math.cos(a)*r*frac, y: cy+Math.sin(a)*r*frac};
  };
  [.25,.5,.75,1].forEach(f => {
    ctx.beginPath();
    for (let i=0; i<n; i++) { const{x,y}=getXY(i,f); i===0?ctx.moveTo(x,y):ctx.lineTo(x,y); }
    ctx.closePath(); ctx.strokeStyle = f===1?'rgba(108,99,255,0.3)':'rgba(255,255,255,0.06)'; ctx.lineWidth=1; ctx.stroke();
  });
  for (let i=0; i<n; i++) {
    const{x,y}=getXY(i,1);
    ctx.beginPath(); ctx.moveTo(cx,cy); ctx.lineTo(x,y);
    ctx.strokeStyle = 'rgba(255,255,255,0.06)'; ctx.lineWidth=1; ctx.stroke();
  }
  const fracs = values.map((v,i) => Math.min(1,v/maxVals[i]));
  ctx.beginPath();
  for (let i=0; i<n; i++) { const{x,y}=getXY(i,fracs[i]); i===0?ctx.moveTo(x,y):ctx.lineTo(x,y); }
  ctx.closePath();
  const g = ctx.createRadialGradient(cx,cy,0,cx,cy,r);
  g.addColorStop(0,'rgba(108,99,255,0.4)'); g.addColorStop(1,'rgba(108,99,255,0.1)');
  ctx.fillStyle=g; ctx.fill();
  ctx.strokeStyle='#6c63ff'; ctx.lineWidth=2; ctx.stroke();
  for (let i=0; i<n; i++) {
    const{x,y}=getXY(i,fracs[i]);
    ctx.beginPath(); ctx.arc(x,y,4,0,Math.PI*2); ctx.fillStyle='#a78bfa'; ctx.fill();
  }
  ctx.font='bold 10px Segoe UI'; ctx.fillStyle='rgba(136,146,176,0.9)'; ctx.textAlign='center';
  for (let i=0; i<n; i++) {
    const{x,y}=getXY(i,1.22);
    ctx.fillText(labels[i], x, y+4);
  }
}

loadDashboard();
