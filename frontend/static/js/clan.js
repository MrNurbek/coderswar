if (!Auth.requireAuth()) throw 0;
Auth.fillUserUI();

const members = [
  {name:'Azizbek T.',handle:'@azizbek',role:'leader',level:'Knight',rating:842,contrib:95,online:true,av:'A',avc:''},
  {name:'Bobur N.',handle:'@bobur_n',role:'officer',level:'Hero',rating:1520,contrib:88,online:true,av:'B',avc:'orange'},
  {name:'Dilnoza K.',handle:'@dilnoza',role:'officer',level:'Warden',rating:610,contrib:72,online:true,av:'D',avc:'green'},
  {name:'Eldor M.',handle:'@eldor_m',role:'member',level:'Knight',rating:780,contrib:65,online:false,av:'E',avc:'red'},
  {name:'Feruza A.',handle:'@feruza',role:'member',level:'Recruit',rating:240,contrib:41,online:true,av:'F',avc:'blue'},
  {name:'Gulnora S.',handle:'@gulnora_s',role:'member',level:'Warden',rating:450,contrib:58,online:false,av:'G',avc:''},
  {name:'Hamid R.',handle:'@hamid_r',role:'member',level:'Knight',rating:820,contrib:70,online:true,av:'H',avc:'orange'},
  {name:'Iroda B.',handle:'@iroda_b',role:'member',level:'Warden',rating:590,contrib:48,online:false,av:'I',avc:'green'},
  {name:'Jasur T.',handle:'@jasur_t',role:'member',level:'Recruit',rating:180,contrib:30,online:false,av:'J',avc:'red'},
  {name:'Kamola M.',handle:'@kamola_m',role:'member',level:'Warden',rating:520,contrib:55,online:true,av:'K',avc:'blue'},
  {name:'Lochin D.',handle:'@lochin',role:'member',level:'Knight',rating:760,contrib:62,online:false,av:'L',avc:''},
  {name:'Nodira O.',handle:'@nodira_o',role:'member',level:'Recruit',rating:290,contrib:25,online:true,av:'N',avc:'orange'},
];

const tbody = document.getElementById('memberBody');
members.forEach(m => {
  const tr = document.createElement('tr');
  const roleClass = m.role==='leader'?'role-leader':m.role==='officer'?'role-officer':'role-member';
  const roleLabel = m.role==='leader'?'Lider':m.role==='officer'?'Ofitser':"A'zo";
  const isMe = m.name === 'Azizbek T.';
  tr.innerHTML = `
    <td><div class="m-info">
      <div class="m-avatar ${m.avc}">${m.av}</div>
      <div>
        <div class="m-name">${m.name}${isMe?' <span style="font-size:.65rem;color:var(--accent)">(men)</span>':''}</div>
        <div class="m-handle">${m.handle}</div>
      </div>
    </div></td>
    <td><span class="role-badge ${roleClass}">${roleLabel}</span></td>
    <td><span class="level-pill">${m.level}</span></td>
    <td style="font-weight:700;color:#a78bfa">${m.rating}</td>
    <td><div class="contrib-bar"><div class="cbar"><div class="cbar-fill" style="width:${m.contrib}%"></div></div><span class="contrib-val">${m.contrib}%</span></div></td>
    <td><span class="online-dot ${m.online?'online':'offline'}"></span>${m.online?'<span style="color:#43e97b;font-size:.8rem">Online</span>':'<span style="color:var(--muted);font-size:.8rem">Offline</span>'}</td>
  `;
  tbody.appendChild(tr);
});

const onlineEl = document.getElementById('onlineMembers');
members.filter(m => m.online).forEach(m => {
  const div = document.createElement('div');
  div.style.cssText = 'display:flex;align-items:center;gap:.7rem;padding:.5rem .6rem;background:rgba(255,255,255,0.03);border-radius:10px';
  div.innerHTML = `<div class="m-avatar ${m.avc}" style="width:30px;height:30px;font-size:.75rem">${m.av}</div>
    <div style="flex:1"><div style="font-size:.83rem;font-weight:600">${m.name}</div><div style="font-size:.72rem;color:var(--accent3)">● Online</div></div>
    <div style="font-size:.75rem;color:var(--muted)">${m.level}</div>`;
  onlineEl.appendChild(div);
});

const challenges = [
  {name:'Code Warriors klani',meta:'Algoritmik urush • 3 masala',time:'2 kun qoldi',active:false},
  {name:'Algo Ninjas klani',meta:'Debug urushi • 5 masala',time:'Bugun 18:00',active:true},
  {name:'DevMasters klani',meta:'Kompleks urush • 5 masala',time:'5 kun qoldi',active:false},
];
const chList = document.getElementById('challengeList');
challenges.forEach(c => {
  chList.innerHTML += `<div class="challenge-item">
    <div class="ch-icon ${c.active?'active':''}">${c.active?'🔥':'⚔️'}</div>
    <div class="ch-info"><div class="ch-name">${c.name}</div><div class="ch-meta">${c.meta}</div></div>
    <div class="ch-time ${c.active?'active':''}">${c.time}</div>
  </div>`;
});

const achieves = [
  {name:"Birinchi g'alaba",desc:'Birinchi klan urushini yutish',pts:'+50 ball',icon:'🏆',cls:'ach-gold',prog:100},
  {name:"5 ketma-ket g'alaba",desc:"5 ta klan urushini ketma-ket yutish",pts:'+120 ball',icon:'🔥',cls:'ach-red',prog:100},
  {name:'100 ta kod topshirish',desc:'Klan ichida 100 ta kod yozish',pts:'+80 ball',icon:'💻',cls:'ach-purple',prog:100},
  {name:'Faol klan',desc:"Bir hafta davomida har kun faol bo'lish",pts:'+60 ball',icon:'⭐',cls:'ach-gold',prog:100},
  {name:"10 ta g'alaba",desc:"Jami 10 ta klan urushini yutish",pts:'+200 ball',icon:'🥇',cls:'ach-gold',prog:100},
  {name:'Klan reytingi Top-5',desc:"Fakultet reytingida Top-5 ga kirish",pts:'+150 ball',icon:'🎯',cls:'ach-green',prog:80},
  {name:'50 ta duel',desc:"Klan a'zolari birgalikda 50 ta duel o'tkazish",pts:'+100 ball',icon:'⚡',cls:'ach-red',prog:72},
  {name:'1000 ta kod',desc:'Klan ichida jami 1000 ta kod yozish',pts:'+300 ball',icon:'🚀',cls:'ach-purple',prog:100},
];
const aList = document.getElementById('achieveList');
achieves.forEach(a => {
  aList.innerHTML += `<div class="achieve-item">
    <div class="ach-icon ${a.cls}">${a.icon}</div>
    <div class="ach-info">
      <div class="ach-name">${a.name}</div>
      <div class="ach-desc">${a.desc}</div>
      ${a.prog<100?`<div class="ach-progress">
        <div class="ach-prog-bar"><div class="ach-prog-fill" style="width:${a.prog}%"></div></div>
        <div class="ach-prog-txt">${a.prog}% bajarildi</div>
      </div>`:''}
    </div>
    <div class="ach-pts">${a.pts}</div>
  </div>`;
});

const chatMessages = [
  {name:'Bobur N.',text:"Bugun algoritmik urush bor, barchani tayyorgarlikka chaqiraman!",time:'14:32',av:'B',avc:'orange'},
  {name:'Dilnoza K.',text:"Ha, men tayyor. Rekursiv masalalarni qaytadan ko'rdim.",time:'14:35',avc:'green',av:'D'},
  {name:'Hamid R.',text:"Stack va Queue masalalarida yordam kerak bo'lsa aytinglar 😊",time:'14:38',av:'H',avc:'orange'},
  {name:'Azizbek T.',text:"Barchasiga omad! Birgalikda yutamiz 💪",time:'14:40',av:'A',avc:''},
  {name:'Kamola M.',text:"Graf algoritmlarini ham ko'rib chiqish kerak, o'tgan urushda muammo bo'ldi.",time:'14:42',av:'K',avc:'blue'},
  {name:'Bobur N.',text:"To'g'ri. Kechqurun 18:00 da group callga chiqamiz, tayyorgarlik ko'ramiz.",time:'14:45',av:'B',avc:'orange'},
];
const chatBox = document.getElementById('chatBox');
chatMessages.forEach(m => {
  chatBox.innerHTML += `<div class="chat-msg">
    <div class="chat-avatar m-avatar ${m.avc}" style="width:28px;height:28px;font-size:.72rem;flex-shrink:0">${m.av}</div>
    <div class="chat-content">
      <div class="chat-header"><span class="chat-name">${m.name}</span><span class="chat-time">${m.time}</span></div>
      <div class="chat-text">${m.text}</div>
    </div>
  </div>`;
});
chatBox.scrollTop = chatBox.scrollHeight;

const _me = Auth.getUser();
let _myClanId = null;

async function sendChat() {
  const inp = document.getElementById('chatInput');
  const msg = inp.value.trim();
  if (!msg || !_myClanId) return;
  inp.value = '';
  try {
    const saved = await api.sendClanMsg(_myClanId, msg);
    const now = new Date();
    const time = now.getHours() + ':' + String(now.getMinutes()).padStart(2,'0');
    const initials = (_me?.full_name || _me?.username || 'U').charAt(0).toUpperCase();
    chatBox.innerHTML += `<div class="chat-msg">
      <div class="chat-avatar m-avatar" style="width:28px;height:28px;font-size:.72rem;flex-shrink:0;background:var(--accent)">${initials}</div>
      <div class="chat-content">
        <div class="chat-header"><span class="chat-name">${_me?.full_name || _me?.username || 'Men'}</span><span class="chat-time">${time}</span></div>
        <div class="chat-text">${saved?.message || msg}</div>
      </div>
    </div>`;
    chatBox.scrollTop = chatBox.scrollHeight;
  } catch(e) {
    alert('Xabar yuborishda xatolik: ' + e.message);
    inp.value = msg;
  }
}

(async function loadMyClan() {
  try {
    const clans = await api.clans();
    if (!clans?.length) return;
    const myClan = clans.find(c => c.my_role);
    if (!myClan) return;
    _myClanId = myClan.id;
    const msgs = await api.clanChat(myClan.id);
    if (msgs?.length) {
      chatBox.innerHTML = '';
      msgs.slice(-30).forEach(m => {
        const time = new Date(m.created_at).toLocaleTimeString('uz', {hour:'2-digit', minute:'2-digit'});
        const init = (m.user.full_name || m.user.username || 'U').charAt(0).toUpperCase();
        chatBox.innerHTML += `<div class="chat-msg">
          <div class="chat-avatar m-avatar" style="width:28px;height:28px;font-size:.72rem;flex-shrink:0">${init}</div>
          <div class="chat-content">
            <div class="chat-header"><span class="chat-name">${m.user.full_name||m.user.username}</span><span class="chat-time">${time}</span></div>
            <div class="chat-text">${m.message}</div>
          </div>
        </div>`;
      });
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  } catch(e) {}
})();

const clans = [
  {name:'Delta Force',tag:'[DLF]',pts:12840,pos:1,trend:'up'},
  {name:'Code Masters',tag:'[CDM]',pts:11200,pos:2,trend:'up'},
  {name:'Logic Legends',tag:'[LGL]',pts:9870,pos:3,trend:'dn'},
  {name:'Alpha Coders',tag:'[ALC]',pts:8420,pos:4,trend:'up',me:true},
  {name:'Beta Devs',tag:'[BTD]',pts:7640,pos:5,trend:'dn'},
  {name:'Cyber Knights',tag:'[CBK]',pts:6980,pos:6,trend:'up'},
  {name:'Pixel Warriors',tag:'[PXW]',pts:6120,pos:7,trend:'dn'},
  {name:'Algo Ninjas',tag:'[ALN]',pts:5840,pos:8,trend:'up'},
  {name:'CS Heroes',tag:'[CSH]',pts:4920,pos:9,trend:'dn'},
  {name:'DevMasters',tag:'[DVM]',pts:4100,pos:10,trend:'dn'},
];
const rl = document.getElementById('clanRankList');
clans.forEach(c => {
  const posClass = c.pos===1?'gold':c.pos===2?'silver':c.pos===3?'bronze':'';
  rl.innerHTML += `<div class="rank-item ${c.me?'highlight':''}">
    <span class="rank-pos ${posClass}">${c.pos===1?'🥇':c.pos===2?'🥈':c.pos===3?'🥉':c.pos}</span>
    <div class="rank-info">
      <div class="rank-name">${c.name} ${c.me?'<span style="font-size:.65rem;color:var(--accent)">(siz)</span>':''}</div>
      <div class="rank-tag">${c.tag}</div>
    </div>
    <span class="rank-pts">${c.pts.toLocaleString()}</span>
    <span class="rank-trend ${c.trend==='up'?'tr-up':'tr-dn'}">${c.trend==='up'?'↑':'↓'}</span>
  </div>`;
});

function switchTab(id) {
  document.querySelectorAll('.tab-btn').forEach((b, i) => {
    const tabs = ['members','wars','achievements','chat','ranking'];
    b.classList.toggle('active', tabs[i] === id);
  });
  document.querySelectorAll('.tab-content').forEach(t => {
    t.classList.toggle('active', t.id === 'tab-' + id);
  });
}

function openModal(id) { document.getElementById(id).classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); }
document.querySelectorAll('.modal-overlay').forEach(m => m.addEventListener('click', function(e) {
  if (e.target === this) this.classList.remove('open');
}));

let _allClans = [];
let _clanSearchTimer = null;
async function loadClansForSearch() {
  if (_allClans.length) return;
  try { _allClans = await api.clans() || []; } catch {}
}
function searchClans(q) {
  const res = document.getElementById('clanSearchResult');
  clearTimeout(_clanSearchTimer);
  if (!q.trim()) { res.innerHTML = ''; return; }
  _clanSearchTimer = setTimeout(() => {
    const filtered = _allClans.filter(c =>
      c.name.toLowerCase().includes(q.toLowerCase()) || c.tag.toLowerCase().includes(q.toLowerCase())
    ).slice(0, 5);
    if (!filtered.length) { res.innerHTML = '<div style="color:var(--muted);font-size:.83rem;padding:.5rem">Klan topilmadi</div>'; return; }
    res.innerHTML = filtered.map(c => `<div class="clan-result-item" onclick="selectClan(${c.id},'${c.name}')">
      <div class="cr-emblem" style="background:rgba(108,99,255,0.1)">${c.emblem||'🏰'}</div>
      <div class="cr-info"><div class="cr-name">${c.name} <span class="cr-tag">${c.tag}</span></div><div class="cr-meta">${c.member_count} a'zo</div></div>
    </div>`).join('');
  }, 300);
}
document.querySelector('[onclick*="warModal"]')?.addEventListener('click', loadClansForSearch);
let selectedClanId = null;
function selectClan(id, name) {
  selectedClanId = id;
  document.getElementById('clanSearchResult').innerHTML = `<div class="clan-result-item" style="border-color:var(--accent3)">
    <div style="color:#43e97b;font-size:1rem">✓</div>
    <div class="cr-info"><div class="cr-name" style="color:#43e97b">${name} tanlandi</div></div>
  </div>`;
}

async function declareWar() {
  if (!selectedClanId) { alert('Raqib klanni tanlang.'); return; }
  const dateInput = document.querySelector('#warModal input[type=datetime-local]');
  const typeSelect = document.querySelector('#warModal select');
  if (!dateInput.value) { alert('Urush sanasini kiriting.'); return; }
  const warTypeMap = {0:'algorithmic', 1:'debug', 2:'complex'};
  const warType = warTypeMap[typeSelect.selectedIndex] || 'algorithmic';
  const btn = document.getElementById('declareWarBtn');
  const alertEl = document.getElementById('warModalAlert');
  btn.disabled = true; btn.textContent = 'Yuborilmoqda...';
  try {
    await api.createClanWar({
      clan2: selectedClanId,
      war_type: warType,
      scheduled_at: new Date(dateInput.value).toISOString(),
    });
    alertEl.style.cssText = 'display:block;background:rgba(67,233,123,0.12);border:1px solid rgba(67,233,123,0.3);color:#43e97b';
    alertEl.textContent = '✅ Urush taklifi yuborildi! Raqib klan lideri qabul qilishi kutilmoqda.';
    btn.textContent = '✅ Yuborildi';
    setTimeout(() => closeModal('warModal'), 2000);
  } catch(e) {
    alertEl.style.cssText = 'display:block;background:rgba(255,101,132,0.12);border:1px solid rgba(255,101,132,0.3);color:#ff6584';
    alertEl.textContent = e.message || 'Xatolik yuz berdi.';
    btn.disabled = false; btn.textContent = "⚔️ Urush e'lon qilish";
  }
}

(function() {
  const c = document.getElementById('clanChart');
  if (!c) return;
  const ctx = c.getContext('2d');
  c.width = c.offsetWidth*2; c.height = c.offsetHeight*2; ctx.scale(2,2);
  const W = c.offsetWidth/2, H = c.offsetHeight/2;
  const data = [62,68,65,72,70,78,74];
  const labels = ['Du','Se','Ch','Pa','Ju','Sh','Ya'];
  const pad = {l:30,r:15,t:10,b:25};
  const iW = W-pad.l-pad.r, iH = H-pad.t-pad.b;
  const min = 50, max = 90;
  ctx.strokeStyle = 'rgba(255,255,255,0.06)'; ctx.lineWidth = 1;
  for (let i=0; i<=4; i++) { const y=pad.t+iH*(1-i/4); ctx.beginPath(); ctx.moveTo(pad.l,y); ctx.lineTo(pad.l+iW,y); ctx.stroke(); }
  const pts = data.map((v,i) => ({x:pad.l+iW*i/(data.length-1), y:pad.t+iH*(1-(v-min)/(max-min))}));
  const grad = ctx.createLinearGradient(0,pad.t,0,pad.t+iH);
  grad.addColorStop(0,'rgba(108,99,255,0.3)'); grad.addColorStop(1,'rgba(108,99,255,0)');
  ctx.beginPath(); ctx.moveTo(pts[0].x,pad.t+iH);
  pts.forEach(p => ctx.lineTo(p.x,p.y));
  ctx.lineTo(pts[pts.length-1].x,pad.t+iH); ctx.closePath();
  ctx.fillStyle = grad; ctx.fill();
  ctx.beginPath(); ctx.strokeStyle = '#6c63ff'; ctx.lineWidth = 2;
  pts.forEach((p,i) => i===0 ? ctx.moveTo(p.x,p.y) : ctx.lineTo(p.x,p.y));
  ctx.stroke();
  pts.forEach(p => { ctx.beginPath(); ctx.arc(p.x,p.y,3,0,Math.PI*2); ctx.fillStyle = '#6c63ff'; ctx.fill(); });
  ctx.fillStyle = 'rgba(136,146,176,0.8)'; ctx.font = '10px Segoe UI'; ctx.textAlign = 'center';
  labels.forEach((l,i) => ctx.fillText(l, pad.l+iW*i/(data.length-1), H-6));
})();

(function() {
  const c = document.getElementById('rankChart');
  if (!c) return;
  const ctx = c.getContext('2d');
  c.width = c.offsetWidth*2; c.height = c.offsetHeight*2; ctx.scale(2,2);
  const W = c.offsetWidth/2, H = c.offsetHeight/2;
  const data = [8,7,6,5,6,5,4];
  const labels = ['Jan','Feb','Mar','Apr','May','Jun','Jul'];
  const pad = {l:30,r:15,t:10,b:25};
  const iW = W-pad.l-pad.r, iH = H-pad.t-pad.b;
  const min = 1, max = 10;
  ctx.strokeStyle = 'rgba(255,255,255,0.06)'; ctx.lineWidth = 1;
  for (let i=0; i<=4; i++) { const y=pad.t+iH*i/4; ctx.beginPath(); ctx.moveTo(pad.l,y); ctx.lineTo(pad.l+iW,y); ctx.stroke(); }
  const pts = data.map((v,i) => ({x:pad.l+iW*i/(data.length-1), y:pad.t+iH*(v-min)/(max-min)}));
  ctx.beginPath(); ctx.strokeStyle = '#ffd700'; ctx.lineWidth = 2;
  pts.forEach((p,i) => i===0 ? ctx.moveTo(p.x,p.y) : ctx.lineTo(p.x,p.y));
  ctx.stroke();
  pts.forEach(p => { ctx.beginPath(); ctx.arc(p.x,p.y,3,0,Math.PI*2); ctx.fillStyle = '#ffd700'; ctx.fill(); });
  ctx.fillStyle = 'rgba(136,146,176,0.8)'; ctx.font = '10px Segoe UI'; ctx.textAlign = 'center';
  labels.forEach((l,i) => ctx.fillText(l, pad.l+iW*i/(data.length-1), H-6));
})();
