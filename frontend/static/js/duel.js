if (!Auth.requireAuth()) throw 0;
Auth.fillUserUI();

let duelWS = null;
let currentDuel = null;
let battleTimerInt = null;
let seconds = 300;
let codeUpdateTimer = null;

function wsBase() {
  const proto = (API_BASE || '').startsWith('https') ? 'wss' : 'ws';
  const host = (API_BASE || window.location.origin).replace(/^https?:\/\//, '').replace(/\/api\/?$/, '');
  return `${proto}://${host}`;
}

async function loadRecentDuels() {
  const RES = {win:{cls:'res-win',lbl:"G'"}, loss:{cls:'res-loss',lbl:'M'}, draw:{cls:'res-draw',lbl:'D'}};
  try {
    const list = await api.duels();
    const arr = Array.isArray(list) ? list : (list.results || []);
    if (!arr.length) {
      document.getElementById('recentDuels').innerHTML = '<div style="color:var(--muted);padding:.8rem;text-align:center">Hali duel o\'ynamagansiz</div>';
      return;
    }
    const me = Auth.getUser()?.username || '';
    document.getElementById('recentDuels').innerHTML = arr.slice(0,6).map(d => {
      const isCh = d.challenger_username === me;
      const opp = isCh ? (d.opponent_username || '?') : (d.challenger_username || '?');
      const win = d.winner_username === me;
      const lose = d.winner_username && d.winner_username !== me;
      const res = !d.winner_username ? 'draw' : (win ? 'win' : 'loss');
      const topic = d.task_title || '—';
      return `<div class="duel-item">
        <div class="di-result ${RES[res].cls}">${RES[res].lbl}</div>
        <div class="di-info"><div class="di-name">⚔️ ${opp}</div><div class="di-meta">${topic}</div></div>
        <div class="di-score" style="color:${res==='win'?'#43e97b':res==='loss'?'#ff6584':'#ffa500'}">${d.status || ''}</div>
      </div>`;
    }).join('');
  } catch {}
}

async function loadDuelLb() {
  try {
    const data = await api.leaderboard();
    const arr = Array.isArray(data) ? data : (data.results || []);
    const me = Auth.getUser()?.username || '';
    document.getElementById('duelLb').innerHTML = arr.slice(0,6).map((d,i) => `
      <div class="dlb-item" style="${d.username===me?'background:rgba(108,99,255,0.08);border:1px solid rgba(108,99,255,0.2);border-radius:10px':''}">
        <div class="dlb-rank" style="color:${i<3?'#ffd700':'var(--muted)'}">${i<3?['🥇','🥈','🥉'][i]:i+1}</div>
        <div class="dlb-av">⚔️</div>
        <div class="dlb-name">${d.full_name || d.username}${d.username===me?' ←':''}</div>
        <div class="dlb-wins">${d.rating_score || 0} ball</div>
      </div>`).join('');
  } catch {}
}

function selectType(i, el) {
  document.querySelectorAll('.dtype-card').forEach(c => c.classList.remove('chosen'));
  el.classList.add('chosen');
}

async function findMatch() {
  document.getElementById('lobbyScreen').style.display = 'none';
  document.getElementById('matchScreen').style.display = 'flex';
  document.getElementById('matchStatus').textContent = 'Duel yaratilmoqda...';
  document.getElementById('oppAvatar').textContent = '?';
  document.getElementById('oppName').textContent = 'Raqib kutilmoqda...';

  try {
    currentDuel = await api.createDuel({});
    if (!currentDuel) throw new Error('Duel yaratilmadi');
    document.getElementById('matchStatus').textContent = 'Raqib kutilmoqda...';
    connectDuelWS(currentDuel.room_id);
    setTimeout(() => {
      if (duelWS && duelWS.readyState === WebSocket.OPEN) {
        duelWS.send(JSON.stringify({ type: 'ready' }));
      }
    }, 2000);
  } catch(e) {
    document.getElementById('matchStatus').textContent = '❌ ' + (e.message || 'Xatolik');
    setTimeout(() => {
      document.getElementById('matchScreen').style.display = 'none';
      document.getElementById('lobbyScreen').style.display = 'block';
    }, 2000);
  }
}

async function cancelMatch() {
  if (duelWS) { duelWS.close(); duelWS = null; }
  if (currentDuel?.id) {
    try { await api.cancelDuel(currentDuel.id); } catch {}
  }
  currentDuel = null;
  document.getElementById('matchScreen').style.display = 'none';
  document.getElementById('lobbyScreen').style.display = 'block';
}

function connectDuelWS(roomId) {
  const token = Auth.getAccess();
  const url = `${wsBase()}/ws/duel/${roomId}/?token=${token}`;
  duelWS = new WebSocket(url);
  duelWS.onopen = () => console.log('[Duel WS] connected');
  duelWS.onmessage = (evt) => {
    let msg; try { msg = JSON.parse(evt.data); } catch { return; }
    handleWSMessage(msg);
  };
  duelWS.onerror = () => showToast('❌ WebSocket xatoligi. Ulanish uzildi.');
  duelWS.onclose = () => console.log('[Duel WS] disconnected');
}

function handleWSMessage(msg) {
  switch (msg.type) {
    case 'connected': console.log('[WS] Connected as', msg.user); break;
    case 'opponent_ready':
      document.getElementById('matchStatus').textContent = 'Raqib tayyor! Jang boshlanmoqda...';
      document.getElementById('oppAvatar').textContent = '⚔️';
      setTimeout(startBattle, 800);
      break;
    case 'opponent_code':
      const oppArea = document.getElementById('oppCode');
      if (oppArea) oppArea.textContent = msg.code || '';
      document.getElementById('oppStatusTxt').textContent = 'Raqib yozmoqda...';
      break;
    case 'opponent_submitted':
      document.getElementById('oppStatusTxt').textContent = '⚡ Raqib submission yubordi!';
      showToast('⚡ Raqib kodni yubordi!');
      break;
    case 'submission_received':
      document.getElementById('bfStatus').textContent = '⏳ Tekshirilmoqda (Judge0)...';
      break;
    case 'duel_result':
      const me = Auth.getUser()?.username || '';
      const isWin = msg.winner === me;
      showResult(isWin, msg);
      break;
    case 'error': showToast('❌ ' + (msg.message || 'Server xatosi')); break;
  }
}

function startBattle() {
  document.getElementById('matchScreen').style.display = 'none';
  document.getElementById('battleScreen').style.display = 'flex';
  if (currentDuel?.task_title) {
    const taskEl = document.getElementById('battleTaskTitle');
    if (taskEl) taskEl.textContent = currentDuel.task_title;
  }
  updateBattleLines();
  startBattleTimer();
  if (duelWS && duelWS.readyState === WebSocket.OPEN) {
    duelWS.send(JSON.stringify({ type: 'ready' }));
  }
}

function startBattleTimer() {
  battleTimerInt = setInterval(() => {
    seconds--;
    const m = Math.floor(seconds/60).toString().padStart(2,'0');
    const s = (seconds%60).toString().padStart(2,'0');
    const el = document.getElementById('battleTimer');
    if (el) { el.textContent = `${m}:${s}`; if(seconds<=60) el.classList.add('warn'); }
    if (seconds <= 0) { clearInterval(battleTimerInt); battleSubmit(); }
  }, 1000);
}

function battleRun() {
  document.getElementById('bfStatus').textContent = 'Ishga tushirilmoqda...';
  setTimeout(() => document.getElementById('bfStatus').textContent = '✅ Sintaksis OK', 800);
}

function battleSubmit() {
  clearInterval(battleTimerInt);
  const code = document.getElementById('battleCode')?.value || '';
  document.getElementById('bfStatus').textContent = '⏳ Yuklanmoqda...';
  if (duelWS && duelWS.readyState === WebSocket.OPEN) {
    duelWS.send(JSON.stringify({ type: 'submit', code }));
  } else { showToast('❌ WebSocket ulanmagan!'); }
}

function battleSurrender() {
  if (!confirm('Taslim bo\'lishni xohlaysizmi?')) return;
  clearInterval(battleTimerInt);
  if (duelWS && duelWS.readyState === WebSocket.OPEN) {
    duelWS.send(JSON.stringify({ type: 'surrender' }));
  }
}

function onCodeChange() {
  updateBattleLines();
  clearTimeout(codeUpdateTimer);
  codeUpdateTimer = setTimeout(() => {
    const code = document.getElementById('battleCode')?.value || '';
    if (duelWS && duelWS.readyState === WebSocket.OPEN) {
      duelWS.send(JSON.stringify({ type: 'code_update', code }));
    }
  }, 500);
}

function showResult(win, msg = {}) {
  clearInterval(battleTimerInt);
  document.getElementById('battleScreen').style.display = 'none';
  document.getElementById('resultScreen').style.display = 'flex';
  const winPts = msg.win_pts || (win ? 12 : 0);
  const losePts = msg.lose_pts || (win ? 0 : 5);
  if (win) {
    document.getElementById('rConfetti').textContent = '🎉';
    document.getElementById('rcTitle').textContent = 'G\'alaba!';
    document.getElementById('rcSub').textContent = 'Siz birinchi bo\'lib vazifani muvaffaqiyatli bajardingiz!';
    document.getElementById('myFinalScore').style.color = '#43e97b';
    document.getElementById('oppFinalScore').style.color = '#ff6584';
    document.getElementById('myFinalScore').textContent = msg.scores?.challenger || 1;
    document.getElementById('oppFinalScore').textContent = msg.scores?.opponent || 0;
    document.querySelectorAll('.rc-reward')[0].querySelector('.rv').textContent = '+'+winPts;
  } else {
    document.getElementById('rConfetti').textContent = '😤';
    document.getElementById('rcTitle').textContent = "Mag'lubiyat";
    document.getElementById('rcSub').textContent = 'Keyingi marta tezroq bo\'ling!';
    document.querySelector('.rc-player:first-child').className = 'rc-player rc-lose';
    document.querySelector('.rc-player:last-child').className = 'rc-player rc-win';
    document.getElementById('myFinalScore').style.color = '#ff6584';
    document.getElementById('oppFinalScore').style.color = '#43e97b';
    document.getElementById('myFinalScore').textContent = msg.scores?.challenger || 0;
    document.getElementById('oppFinalScore').textContent = msg.scores?.opponent || 1;
    document.querySelectorAll('.rc-reward')[0].querySelector('.rv').textContent = '-'+losePts;
  }
  if (duelWS) { duelWS.close(); duelWS = null; }
}

function playAgain() {
  document.getElementById('resultScreen').style.display = 'none';
  document.getElementById('lobbyScreen').style.display = 'block';
  seconds = 300; currentDuel = null;
}

function showToast(msg) {
  const t = document.createElement('div');
  t.style.cssText = 'position:fixed;bottom:1.5rem;right:1.5rem;background:#1a1f3a;border:1px solid rgba(255,101,132,0.4);border-radius:14px;padding:.75rem 1.2rem;font-size:.85rem;font-weight:600;z-index:999;animation:fi .3s ease;box-shadow:0 8px 30px rgba(0,0,0,.3)';
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 2800);
}
const _s = document.createElement('style');
_s.textContent = '@keyframes fi{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}';
document.head.appendChild(_s);

function updateBattleLines() {
  const ta = document.getElementById('battleCode');
  const ln = document.getElementById('beLn');
  if (ta && ln) ln.innerHTML = ta.value.split('\n').map((_,i) => `<span>${i+1}</span>`).join('');
}

function handleBattleTab(e) {
  if (e.key === 'Tab') {
    e.preventDefault();
    const t = e.target;
    const s = t.selectionStart;
    t.value = t.value.substring(0,s) + '    ' + t.value.substring(t.selectionEnd);
    t.selectionStart = t.selectionEnd = s + 4;
    updateBattleLines();
  }
}

(async function init() {
  await Promise.all([loadRecentDuels(), loadDuelLb()]);
  updateBattleLines();
})();
