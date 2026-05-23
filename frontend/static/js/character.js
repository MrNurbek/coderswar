if (!Auth.requireAuth()) throw 0;
const CHARS=[
  {id:'warrior',name:'Jangchi',en:'Warrior',avatar:'⚔️',tag:'tag-warrior',
   desc:'Kuch va qat\'iyat timsoli. Qiyin vazifalardan qo\'rqmaydi. Har qanday muammoni to\'g\'ridan-to\'g\'ri hal qiladi.',
   weapons:['⚔️ Sword','🏹 Spear','🛡️ Armor'],
   stats:{strength:95,speed:60,intelligence:65,defense:80}},
  {id:'ranger',en:'Ranger',name:'Sarguzashtchi',avatar:'🏹',tag:'tag-ranger',
   desc:'Tezkorlik va aniqlik timsoli. Eng samarali va qisqa yechim topadi. Kodni optimallashtirishda tengsiz.',
   weapons:['🏹 Spear','👟 Boots','🥋 Light Armor'],
   stats:{strength:65,speed:95,intelligence:75,defense:55}},
  {id:'sorceress',name:'Sehrgar Ayol',en:'Sorceress',avatar:'🔮',tag:'tag-sorceress',
   desc:'Bilim va sehrli tafakkur timsoli. Algoritmlarni sehrga aylantiradi. Kreativ yechimlar topishda ustun.',
   weapons:['🪄 Wand','💍 Ring'],
   stats:{strength:45,speed:70,intelligence:98,defense:50}},
  {id:'knight',name:'Ritsar',en:'Knight',avatar:'🛡️',tag:'tag-knight',
   desc:'Adolat va himoya timsoli. Jamoani boshqaradi. Murakkab loyihalarni tartibli hal qiladi.',
   weapons:['⚔️ Sword','🛡️ Shield','🏰 Armor'],
   stats:{strength:80,speed:55,intelligence:70,defense:95}},
  {id:'ladyknight',name:'Ayol Ritsar',en:'Lady Knight',avatar:'⚜️',tag:'tag-ladyknight',
   desc:'Qat\'iyat va himoya timsoli. Barcha cheklovlarni engib o\'tadi. Kuch va aql muvozanatini saqlaydi.',
   weapons:['⚔️ Sword','🛡️ Shield','🏰 Armor','💍 Ring'],
   stats:{strength:78,speed:72,intelligence:78,defense:88}}
];

const STAT_COLORS={strength:'#ef4444',speed:'#22c55e',intelligence:'#a855f7',defense:'#3b82f6'};
const STAT_LABELS={strength:'Kuch',speed:'Tezlik',intelligence:'Intellekt',defense:'Himoya'};

let chosen=null;

function renderChars(){
  const grid=document.getElementById('charsGrid');
  grid.innerHTML=CHARS.map(c=>`
    <div class="char-card c-${c.id}" id="card-${c.id}" onclick="pick('${c.id}')">
      <div class="selected-badge">✓ Tanlandi</div>
      <span class="char-avatar">${c.avatar}</span>
      <div class="char-name">${c.name}</div>
      <div class="char-en">${c.en}</div>
      <span class="char-tag ${c.tag}">${c.en}</span>
      <div class="char-desc">${c.desc.split('.')[0]}.</div>
      <div class="char-stats">
        ${Object.entries(c.stats).map(([k,v])=>`
          <div class="cstat">
            <span class="cstat-label">${STAT_LABELS[k].slice(0,4)}</span>
            <div class="cstat-bar"><div class="cstat-fill" style="width:${v}%;background:${STAT_COLORS[k]}"></div></div>
          </div>`).join('')}
      </div>
    </div>`).join('');
}

function pick(id){
  chosen=id;
  document.querySelectorAll('.char-card').forEach(c=>c.classList.remove('active'));
  document.getElementById('card-'+id).classList.add('active');
  const c=CHARS.find(x=>x.id===id);
  document.getElementById('dpAvatar').textContent=c.avatar;
  document.getElementById('dpName').textContent=c.name;
  document.getElementById('dpEn').textContent=c.en;
  document.getElementById('dpDesc').textContent=c.desc;
  document.getElementById('dpWeapons').innerHTML=c.weapons.map(w=>`<span class="weapon-chip">${w}</span>`).join('');
  document.getElementById('dpStats').innerHTML=Object.entries(c.stats).map(([k,v])=>`
    <div class="dp-stat">
      <div class="dsv" style="color:${STAT_COLORS[k]}">${v}</div>
      <div class="dsl">${STAT_LABELS[k]}</div>
    </div>`).join('');
  const panel=document.getElementById('detailPanel');
  panel.classList.add('show');
  panel.scrollIntoView({behavior:'smooth',block:'nearest'});
  const btn=document.getElementById('confirmBtn');
  btn.classList.add('ready');
  btn.textContent=`${c.avatar} ${c.name}ni tanlash →`;
  document.getElementById('confirmHint').textContent=`${c.name} (${c.en}) tanlandi`;
}

async function confirm(){
  if(!chosen) return;
  const c=CHARS.find(x=>x.id===chosen);
  document.getElementById('confirmBtn').textContent='Saqlanmoqda...';
  document.getElementById('confirmBtn').classList.remove('ready');
  try {
    await api.patch('/auth/me/', { character: chosen });
    const user = Auth.getUser();
    if (user && user.student_profile) {
      user.student_profile.character = chosen;
      Auth.setUser(user);
    }
  } catch(e) { /* character field optional */ }
  window.location.href = 'dashboard.html';
}

renderChars();
