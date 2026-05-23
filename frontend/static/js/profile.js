if (!Auth.requireAuth()) throw 0;

function showTab(id, el) {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('show'));
  document.querySelectorAll('.ptab').forEach(t => t.classList.remove('active'));
  document.getElementById('tab-' + id).classList.add('show');
  el.classList.add('active');
}

function drawRadar(vals) {
  const c = document.getElementById('radarFull');
  if (!c) return;
  const ctx = c.getContext('2d');
  ctx.clearRect(0, 0, c.width, c.height);
  const W=c.width, H=c.height, cx=W/2, cy=H/2, r=Math.min(W,H)/2-36;
  const labels = ['Motivatsion','Kognitiv','Faoliyatli','Adaptiv','Kreativlik','Refleksiv'];
  const maxV   = [10, 20, 30, 15, 15, 10];
  const n = labels.length;
  function xy(i,f){ const a=(-Math.PI/2)+(i/n)*2*Math.PI; return{x:cx+Math.cos(a)*r*f,y:cy+Math.sin(a)*r*f}; }
  [.25,.5,.75,1].forEach(f=>{
    ctx.beginPath();
    for(let i=0;i<n;i++){const{x,y}=xy(i,f);i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);}
    ctx.closePath();ctx.strokeStyle=f===1?'rgba(108,99,255,0.3)':'rgba(255,255,255,0.05)';ctx.lineWidth=1;ctx.stroke();
  });
  for(let i=0;i<n;i++){const{x,y}=xy(i,1);ctx.beginPath();ctx.moveTo(cx,cy);ctx.lineTo(x,y);ctx.strokeStyle='rgba(255,255,255,0.05)';ctx.lineWidth=1;ctx.stroke();}
  const fracs = vals.map((v,i)=>Math.min(v/maxV[i],1));
  ctx.beginPath();
  for(let i=0;i<n;i++){const{x,y}=xy(i,fracs[i]);i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);}
  ctx.closePath();
  const g=ctx.createRadialGradient(cx,cy,0,cx,cy,r);
  g.addColorStop(0,'rgba(108,99,255,0.45)');g.addColorStop(1,'rgba(108,99,255,0.08)');
  ctx.fillStyle=g;ctx.fill();ctx.strokeStyle='#6c63ff';ctx.lineWidth=2;ctx.stroke();
  for(let i=0;i<n;i++){const{x,y}=xy(i,fracs[i]);ctx.beginPath();ctx.arc(x,y,5,0,Math.PI*2);ctx.fillStyle='#a78bfa';ctx.fill();}
  ctx.font='bold 10px Segoe UI';ctx.fillStyle='rgba(136,146,176,.9)';ctx.textAlign='center';
  for(let i=0;i<n;i++){const{x,y}=xy(i,1.25);ctx.fillText(labels[i],x,y+4);}
}

function drawCriteriaBreakdown(vals) {
  const CRIT = [
    {n:'🔥 Motivatsion',max:10,c:'#6c63ff'},
    {n:'🧠 Kognitiv',   max:20,c:'#4299e1'},
    {n:'💻 Faoliyatli', max:30,c:'#43e97b'},
    {n:'🎯 Adaptiv',    max:15,c:'#ffa500'},
    {n:'✨ Kreativlik', max:15,c:'#ff6584'},
    {n:'🔄 Refleksiv',  max:10,c:'#ed8936'},
  ];
  document.getElementById('criteriaBreakdown').innerHTML = CRIT.map((c,i)=>`
    <div style="display:flex;align-items:center;gap:.8rem;margin-bottom:.9rem">
      <div style="font-size:.82rem;color:var(--muted);width:110px;flex-shrink:0">${c.n}</div>
      <div style="flex:1;height:8px;background:rgba(255,255,255,0.07);border-radius:4px;overflow:hidden">
        <div style="width:${Math.min(vals[i]/c.max*100,100)}%;height:100%;border-radius:4px;background:${c.c}"></div>
      </div>
      <div style="font-size:.82rem;font-weight:700;color:${c.c};min-width:54px;text-align:right">${+(vals[i]||0).toFixed(1)}/${c.max}</div>
    </div>`).join('');
}

const CHAR_DATA = {
  warrior:    {avatar:'⚔️', name:'Jangchi',      en:'Warrior',    weapons:['⚔️ Qilich','🏹 Nayza','🛡️ Zirh']},
  ranger:     {avatar:'🏹', name:'Sarguzashtchi', en:'Ranger',     weapons:['🏹 Nayza','👟 Etik','🥋 Engil Zirh']},
  sorceress:  {avatar:'🔮', name:'Sehrgar Ayol',  en:'Sorceress',  weapons:['🪄 Tayoqcha','💍 Uzuk']},
  knight:     {avatar:'🛡️', name:'Ritsar',        en:'Knight',     weapons:['⚔️ Qilich','🛡️ Qalqon','🏰 Zirh']},
  ladyknight: {avatar:'⚜️', name:'Ayol Ritsar',   en:'Lady Knight',weapons:['⚔️ Qilich','🛡️ Qalqon','🏰 Zirh','💍 Uzuk']},
};
const LEVEL_META = {
  recruit:    {icon:'🛡️', name:'Recruit'},
  warden:     {icon:'🗡️', name:'Warden'},
  knight:     {icon:'⚔️', name:'Knight'},
  hero:       {icon:'🦅', name:'Hero'},
  legend:     {icon:'🔥', name:'Legend'},
  lord:       {icon:'👑', name:'Lord'},
  deity:      {icon:'🔮', name:'Deity'},
  titan:      {icon:'⚡', name:'Titan'},
};
function _relDate(iso) {
  if (!iso) return '';
  const d = Math.floor((Date.now() - new Date(iso)) / 86400000);
  if (d === 0) return 'Bugun';
  if (d === 1) return 'Kecha';
  if (d < 7)  return d + ' kun avval';
  if (d < 30) return Math.floor(d/7) + ' hafta avval';
  return Math.floor(d/30) + ' oy avval';
}

async function initProfile() {
  Auth.fillUserUI();
  try {
    const [me, scores, badges, reflections, inventory] = await Promise.all([
      api.me(),
      api.scores(),
      api.myBadges(),
      api.reflections(),
      api.inventory().catch(() => []),
    ]);
    Auth.setUser(me);
    const sp = me.student_profile || {};
    const lv = LEVEL_META[sp.level] || {icon:'⚔️', name: sp.level || 'Student'};

    const initials = (me.first_name||me.username||'?')[0].toUpperCase();
    document.getElementById('phAvatar').textContent = initials;

    const ch = CHAR_DATA[sp.character] || CHAR_DATA.warrior;
    document.getElementById('phChar').textContent = ch.avatar;

    document.getElementById('phCharAva').textContent   = ch.avatar;
    document.getElementById('phCharName').textContent  = `${ch.name} · ${ch.en}`;
    document.getElementById('phCharWeapons').innerHTML =
      ch.weapons.map(w => `<span class="w-chip">${w}</span>`).join('');
    document.getElementById('phCharBlock').style.display = 'flex';
    document.getElementById('phName').textContent   = `${me.first_name||''} ${me.last_name||''}`.trim() || me.username;

    const metaParts = [
      sp.university && `🏫 ${sp.university}`,
      sp.direction  && `📚 ${sp.direction}`,
      sp.year       && `📅 ${sp.year}-kurs`,
      sp.group      && `👥 ${sp.group}`,
      me.phone      && `📞 ${me.phone}`,
    ].filter(Boolean);
    document.getElementById('phMeta').innerHTML = metaParts.map(p=>`<span>${p}</span>`).join('') || '<span>—</span>';

    const completedTopics = Array.isArray(scores) ? scores.filter(s=>s.is_completed).length : 0;
    document.getElementById('phTags').innerHTML = `
      <span class="ph-tag t-level">${lv.icon} ${lv.name}</span>
      ${sp.current_streak ? `<span class="ph-tag t-streak">🔥 ${sp.current_streak} kun streak</span>` : ''}
      <span class="ph-tag" style="background:rgba(67,233,123,0.1);border-color:rgba(67,233,123,0.25);color:#43e97b">✅ ${completedTopics}/45 mavzu</span>`;
    document.getElementById('phBio').textContent = sp.bio || me.bio || '';

    const rating  = sp.rating_score || 0;
    const academic = sp.academic_score ? Math.round(sp.academic_score*10)/10 : '—';
    document.getElementById('phRating').textContent   = rating;
    document.getElementById('phAcademic').textContent = academic;
    document.getElementById('phBadges').textContent   = Array.isArray(badges) ? badges.length : '—';
    document.getElementById('phDuels').textContent    = sp.duels_won || 0;

    document.getElementById('ovRating').textContent   = rating;
    document.getElementById('ovAcademic').textContent = academic;
    document.getElementById('ovProgress').textContent = Math.round(completedTopics/45*100) + '%';
    document.getElementById('ovStreak').textContent   = sp.current_streak || 0;

    if (Array.isArray(scores) && scores.length) {
      const avg = key => scores.reduce((s,sc) => s+(sc[key]||0), 0) / scores.length;
      const radarVals = [avg('mo_score'), avg('ko_score'), avg('fa_score'), avg('ad_score'), avg('kr_score'), avg('re_score')];
      drawRadar(radarVals);
      drawCriteriaBreakdown(radarVals);
    } else {
      drawRadar([0,0,0,0,0,0]);
      drawCriteriaBreakdown([0,0,0,0,0,0]);
    }

    const scColor2 = s => s>=85?'#43e97b':s>=70?'#4299e1':s>=60?'#ffa500':'#ff6584';
    const sortedScores = Array.isArray(scores) ? [...scores].sort((a,b)=>(a.topic_number||a.topic||0)-(b.topic_number||b.topic||0)) : [];
    document.getElementById('trajBody').innerHTML = sortedScores.length
      ? sortedScores.map((s,i) => `
          <div class="tt-row">
            <div style="color:var(--muted)">${s.topic_number || (i+1)}</div>
            <div style="font-size:.85rem;font-weight:500">${s.topic_title || s.topic_name || `Mavzu ${i+1}`}</div>
            <div class="tsc" style="color:${scColor2(s.total_score||0)}">${Math.round(s.total_score||0)}</div>
            <div class="tsc" style="color:#6c63ff">${s.mo_score||0}</div>
            <div class="tsc" style="color:#4299e1">${s.ko_score||0}</div>
            <div class="tsc" style="color:#43e97b">${s.fa_score||0}</div>
            <div class="tsc" style="color:#ffa500">${(s.ad_score||0)+(s.kr_score||0)}</div>
            <div class="tsc" style="color:#ed8936">${s.re_score||0}</div>
          </div>`).join('')
      : '<div style="text-align:center;padding:2rem;color:var(--muted)">Hali topshiriqlar bajarilmagan</div>';

    const typeMap = {exercise:'type-assign Topshiriq', project:'type-mini Mini-loyiha'};
    const PORT_SCORES = (Array.isArray(scores) ? scores.filter(s=>s.is_completed) : []).slice(0, 12);
    document.getElementById('portfolioGrid').innerHTML = PORT_SCORES.length
      ? PORT_SCORES.map(s => {
          const [cls, lbl] = (typeMap.exercise).split(' ');
          return `<div class="port-card">
            <div class="pc-top"><div class="pc-icon">✅</div><span class="pc-type ${cls}">${lbl}</span></div>
            <div class="pc-title">${s.topic_title || s.topic_name || `Mavzu ${s.topic}`}</div>
            <div class="pc-topic">${s.total_score || 0} / 100 ball</div>
            <div class="pc-tags"><span class="pc-tag">C#</span></div>
            <div class="pc-bottom"><span>${_relDate(s.updated_at || s.created_at)}</span><span class="pc-score">+${Math.round(s.total_score||0)} ball</span></div>
          </div>`;
        }).join('')
      : '<div style="text-align:center;padding:2rem;color:var(--muted)">Hali yakunlangan mavzu yo\'q</div>';

    const earnedBadges  = Array.isArray(badges) ? badges.map(ub => ub.badge || ub).filter(Boolean) : [];
    const lockedBadges  = [{icon:'📚',name:'Bookworm',desc:'5 mavzu yakunla'},{icon:'🎯',name:'Perfectionist',desc:'Mavzu 100 ball'},{icon:'🚀',name:'Rocket',desc:'1000 Rating score'},{icon:'👑',name:'Legend',desc:'Legend levelga yet'},{icon:'🏰',name:'Clan Lord',desc:'Clan yasat'},{icon:'🔮',name:'Sorcerer',desc:'AI tahlil top'}];
    document.getElementById('badgesFull').innerHTML = [
      ...earnedBadges.map(b=>`
        <div class="bf-item">
          <div class="bf-icon">${b.icon || b.emoji || '🏅'}</div>
          <div class="bf-name">${b.name}</div>
          <div class="bf-desc">${b.description || b.desc || ''}</div>
          <div class="bf-date">${_relDate(b.earned_at || b.created_at)}</div>
        </div>`),
      ...lockedBadges.map(b=>`
        <div class="bf-item locked">
          <div class="bf-icon">${b.icon}</div>
          <div class="bf-name">${b.name}</div>
          <div class="bf-desc">${b.desc}</div>
          <div class="bf-date" style="color:var(--muted)">🔒 Qulflangan</div>
        </div>`),
    ].join('');

    const reflArr = Array.isArray(reflections) ? reflections : (reflections.results || []);
    document.getElementById('reflList').innerHTML = reflArr.length
      ? reflArr.map(r => `
          <div class="refl-item">
            <div class="ri-top">
              <span class="ri-topic">${r.topic_title || r.topic_name || `Mavzu ${r.topic}`}</span>
              <span class="ri-score">Re: ${r.re_score||r.score||'—'}/10</span>
              <span class="ri-date">${_relDate(r.created_at)}</span>
            </div>
            <div class="ri-text">${r.text || r.content || ''}</div>
          </div>`).join('')
      : '<div style="text-align:center;padding:2rem;color:var(--muted)">Hali refleksiya yozilmagan</div>';

    renderInventory(Array.isArray(inventory) ? inventory : (inventory.results || []));

  } catch(e) {
    console.error('Profile yuklanmadi:', e);
  }
}

const RARITY_COLORS = {
  common:'#94a3b8', rare:'#4299e1', epic:'#a855f7', legendary:'#ffd700'
};
const RARITY_UZ = {
  common:'Oddiy', rare:'Noyob', epic:'Epic', legendary:'Afsonaviy'
};
const TYPE_UZ = {
  weapon:'Qurol', armor:'Zirh', ring:'Uzuk', boots:'Etik'
};

function renderInventory(items) {
  const grid = document.getElementById('invGrid');
  if (!grid) return;

  if (!items.length) {
    grid.innerHTML = '<div style="text-align:center;padding:3rem;color:var(--muted);grid-column:1/-1">⚔️ Hali qurol-aslaha topilmagan.<br><small>Topshiriq va loyihalarni bajaring!</small></div>';
    return;
  }

  const atk = items.filter(i=>i.is_equipped).reduce((s,i)=>s+(i.equipment.attack_bonus||0),0);
  const def = items.filter(i=>i.is_equipped).reduce((s,i)=>s+(i.equipment.defense_bonus||0),0);
  const bar = document.getElementById('equippedBonusBar');
  if (bar) {
    bar.style.display = 'flex';
    document.getElementById('invAtkBonus').textContent = `+${atk}% Hujum`;
    document.getElementById('invDefBonus').textContent = `+${def}% Himoya`;
  }

  grid.innerHTML = items.map(ue => {
    const eq = ue.equipment;
    const col = RARITY_COLORS[eq.rarity] || '#94a3b8';
    return `
    <div class="inv-card ${ue.is_equipped?'equipped':''}" style="border-color:${ue.is_equipped?col:'rgba(255,255,255,0.07)'}">
      ${ue.is_equipped ? '<span class="inv-equipped-badge">KIYILGAN</span>' : ''}
      <span class="inv-icon">${eq.icon}</span>
      <div class="inv-name">${eq.name}</div>
      <div class="inv-rarity" style="color:${col}">${RARITY_UZ[eq.rarity]||eq.rarity} · ${TYPE_UZ[eq.eq_type]||eq.eq_type}</div>
      <div class="inv-stats">
        ${eq.attack_bonus  ? `⚔️ +${eq.attack_bonus}% hujum<br>` : ''}
        ${eq.defense_bonus ? `🛡️ +${eq.defense_bonus}% himoya<br>` : ''}
        <span style="font-size:.68rem">${eq.description}</span>
      </div>
      <button class="inv-equip-btn ${ue.is_equipped?'on':''}"
        onclick="toggleEquip(${ue.id}, ${ue.is_equipped}, this)">
        ${ue.is_equipped ? '✓ Kiyilgan — Yechish' : '▶ Kiyish'}
      </button>
    </div>`;
  }).join('');
}

async function toggleEquip(ueId, isEquipped, btn) {
  btn.disabled = true;
  try {
    const action = isEquipped ? 'unequip' : 'equip';
    await api.equipItem(ueId, action);
    const inv = await api.inventory().catch(()=>[]);
    renderInventory(Array.isArray(inv) ? inv : []);
  } catch(e) {
    btn.disabled = false;
  }
}

async function handleAvatarUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  if (file.size > 2 * 1024 * 1024) {
    alert('Fayl hajmi 2MB dan oshmasligi kerak.');
    return;
  }

  const avatarEl = document.getElementById('phAvatar');
  const origContent = avatarEl.textContent;
  avatarEl.textContent = '⏳';

  try {
    const result = await api.uploadAvatar(file);

    const img = document.createElement('img');
    img.src = result.avatar;
    img.style.cssText = 'width:100%;height:100%;object-fit:cover;border-radius:50%';
    avatarEl.textContent = '';
    avatarEl.appendChild(img);

    const user = Auth.getUser();
    if (user) { user.avatar = result.avatar; Auth.setUser(user); }

    const toast = document.createElement('div');
    toast.textContent = '✅ Avatar yangilandi!';
    toast.style.cssText = 'position:fixed;bottom:1.5rem;right:1.5rem;background:#43e97b;color:#0a0e1a;padding:.7rem 1.2rem;border-radius:12px;font-weight:700;z-index:9999;animation:fadeIn .3s';
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2500);
  } catch(e) {
    avatarEl.textContent = origContent;
    alert(e.message || 'Avatar yuklashda xatolik.');
  }

  event.target.value = '';
}

initProfile();
