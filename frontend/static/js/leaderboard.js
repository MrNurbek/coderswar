const LEVEL_NAMES  = ['Recruit','Warden','Knight','Hero','Legend','Lord','Deity','Titan'];
const LEVEL_COLORS = ['#94a3b8','#43e97b','#4299e1','#a78bfa','#ffa500','#ff6584','#f07167','#ffd700'];
const LEVEL_ICONS  = ['🛡️','🗡️','⚔️','🦅','🔥','👑','🔮','⚡'];

let allData = [];
let myId = null;

function _levelIdx(rating) {
  return rating>=4051?7:rating>=3351?6:rating>=2601?5:rating>=1901?4:rating>=1301?3:rating>=751?2:rating>=301?1:0;
}

function _mapEntry(entry, rank, myUserId) {
  const sp = entry.student_profile || {};
  const rating = sp.rating_score || entry.rating_score || 0;
  const acad = sp.academic_score || entry.academic_score || 0;
  const streak = sp.current_streak || entry.current_streak || 0;
  const level = sp.level || entry.level || '';
  const lvIdx = _levelIdx(rating);
  const name = entry.full_name || (entry.first_name ? `${entry.first_name} ${(entry.last_name||'')[0] || ''}.` : entry.username);
  const univ = sp.university || entry.university || '';
  const group = sp.group || entry.group || '';
  return { rank, name, rating, academic: Math.round(acad), level: lvIdx, levelName: level || LEVEL_NAMES[lvIdx],
           icon: LEVEL_ICONS[lvIdx], univ, group, streak, me: entry.id === myUserId };
}

function renderPodium(data) {
  const top3 = data.slice(0, 3);
  if (top3.length < 3) { document.getElementById('podiumEl').innerHTML = ''; return; }
  const order = [1, 0, 2];
  const slots = ['p2','p1','p3'];
  const labels = ["🥈 2-o'rin","🥇 1-o'rin","🥉 3-o'rin"];
  document.getElementById('podiumEl').innerHTML = order.map((di, si) => {
    const d = top3[di];
    if (!d) return '';
    const lc = LEVEL_COLORS[d.level];
    return `<div class="podium-slot ${slots[si]}">
      <div class="pod-avatar">${si===1?'<div class="pod-crown">👑</div>':''}${d.icon}</div>
      <div class="pod-name">${d.name}</div>
      <div class="pod-score">⭐ ${d.rating.toLocaleString()} ball</div>
      <div class="pod-level" style="color:${lc}">${d.levelName}</div>
      <div class="pod-bar">${labels[si]}</div>
    </div>`;
  }).join('');
}

function renderTable(data) {
  if (!data.length) {
    document.getElementById('lbBody').innerHTML = '<div style="text-align:center;padding:2rem;color:var(--muted)">Natija topilmadi</div>';
    return;
  }
  document.getElementById('lbBody').innerHTML = data.map(d => {
    const lc = LEVEL_COLORS[d.level];
    const ac = d.academic >= 80 ? 'ac-high' : d.academic >= 65 ? 'ac-mid' : 'ac-low';
    return `<div class="lb-row ${d.me?'me':''}" onclick="window.location.href='profile.html'">
      <div class="rank-num ${d.rank<=3?'rank-'+d.rank:'rank-other'}">${d.rank<=3?['🥇','🥈','🥉'][d.rank-1]:d.rank}</div>
      <div class="user-cell">
        <div class="user-av" style="background:${lc}22;border-color:${lc}55">${d.icon}</div>
        <div>
          <div class="user-name">${d.name}${d.me?' <span style="background:rgba(108,99,255,0.2);color:#a78bfa;font-size:.65rem;padding:.1rem .4rem;border-radius:5px;margin-left:.3rem">Sen</span>':''}</div>
          <div class="user-meta">${[d.univ, d.group].filter(Boolean).join(' · ')}${d.streak?' · 🔥 '+d.streak+' kun':''}</div>
        </div>
      </div>
      <div class="score-cell">⭐ ${d.rating.toLocaleString()}</div>
      <div class="academic-cell ${ac}">${d.academic}/100</div>
      <div><span class="level-badge" style="background:${lc}22;color:${lc}">${d.levelName}</span></div>
      <div class="trend-cell"><span class="t-same">— Barqaror</span></div>
    </div>`;
  }).join('');
}

function filterBy(type, el) {
  document.querySelectorAll('.ftab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  let data = [...allData];
  if (type === 'week') data = [...data].sort((a,b) => b.streak - a.streak);
  renderTable(data.slice(0, 30));
}

function searchTable(q) {
  const d = q ? allData.filter(r => r.name.toLowerCase().includes(q.toLowerCase())) : allData;
  renderTable(d.slice(0, 30));
}

async function initLeaderboard() {
  Auth.fillUserUI();
  try {
    const me = await api.me();
    myId = me.id;
    const sp = me.student_profile || {};
    document.getElementById('myRankAv').textContent = (me.first_name||me.username||'?')[0].toUpperCase();
    document.getElementById('myRankName').innerHTML = `${me.first_name || ''} ${me.last_name || ''} <span style="font-size:.8rem">⚔️</span>`.trim();
    document.getElementById('myRankScore').textContent = sp.rating_score || '—';
    document.getElementById('myRankAcad').textContent = sp.academic_score ? Math.round(sp.academic_score) : '—';
    const streak = sp.current_streak || 0;
    const level = sp.level || '';
    document.getElementById('myRankMeta').textContent = [level, sp.university, sp.group, streak ? '🔥 '+streak+' kun' : ''].filter(Boolean).join(' · ');
  } catch(e) {}

  try {
    document.getElementById('lbBody').innerHTML = '<div style="text-align:center;padding:2rem;color:var(--muted)">⏳ Yuklanmoqda...</div>';
    const res = await api.leaderboard();
    const raw = Array.isArray(res) ? res : (res.results || []);
    allData = raw.map((entry, i) => _mapEntry(entry, i+1, myId));
    const myEntry = allData.find(d => d.me);
    if (myEntry) {
      document.getElementById('myRankNum').textContent = '#' + myEntry.rank;
      document.getElementById('myRankBar').style.display = 'flex';
    }
    renderPodium(allData);
    renderTable(allData.slice(0, 30));
    document.querySelector('.bc').textContent = `Dashboard › Reyting · ${allData.length} talaba`;
  } catch(e) {
    document.getElementById('lbBody').innerHTML = `<div style="text-align:center;padding:2rem;color:#ff8fab">❌ Yuklab bo'lmadi: ${e.message}</div>`;
  }
}

if (!Auth.requireAuth()) throw 0;
initLeaderboard();
