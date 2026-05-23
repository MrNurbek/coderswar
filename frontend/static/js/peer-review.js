if (!Auth.requireAuth()) throw 0;
Auth.fillUserUI();

let _queueData = [];
let _myRevData = [];
let _fbData    = [];
let _lbData    = [];
let activeTopicScoreId = null;
let selectedStars = 3;

const criteria = [
  {name:'Kognitiv (Ko)', max:20, key:'ko_score'},
  {name:'Faoliyat (Fa)', max:30, key:'fa_score'},
  {name:'Adaptiv (Ad)',  max:15, key:'ad_score'},
  {name:'Kreativ (Kr)',  max:15, key:'kr_score'},
  {name:'Reflektiv (Re)',max:10, key:'re_score'},
];
const scores = {ko_score:0, fa_score:0, ad_score:0, kr_score:0, re_score:0};

const $ = id => document.getElementById(id);
function setText(id, v) { const el = $(id); if (el) el.textContent = v; }
function fmtDate(s) {
  if (!s) return '';
  return new Date(s).toLocaleDateString('uz-UZ', {day:'numeric', month:'short'});
}
function avatarColors(idx) {
  const cs = [
    'linear-gradient(135deg,#6c63ff,#ff6584)',
    'linear-gradient(135deg,#43e97b,#38f9d7)',
    'linear-gradient(135deg,#f97316,#ffd700)',
    'linear-gradient(135deg,#4facfe,#00f2fe)',
    'linear-gradient(135deg,#ff6584,#ff416c)',
  ];
  return cs[idx % cs.length];
}
function levelLabel(l) {
  return l === 'beginner' ? "Boshlang'ich" : l === 'intermediate' ? "O'rta" : 'Yuqori';
}

(async () => {
  try {
    const [queue, given, received, lb] = await Promise.all([
      api.peerReviewQueue().catch(() => []),
      api.myReviews('given').catch(() => []),
      api.myReviews('received').catch(() => []),
      api.peerReviewLeaderboard().catch(() => []),
    ]);

    _queueData = Array.isArray(queue)    ? queue    : (queue.results    || []);
    _myRevData = Array.isArray(given)    ? given    : (given.results    || []);
    _fbData    = Array.isArray(received) ? received : (received.results || []);
    _lbData    = Array.isArray(lb)       ? lb       : (lb.results       || []);

    renderStats();
    renderQueue();
    renderMyReviews();
    renderReceived();
    renderLeaderboard();
  } catch(e) {
    console.error('Peer review data yuklanmadi:', e);
  }
})();

function renderStats() {
  const qN = _queueData.length;
  setText('statGiven',    _myRevData.length);
  setText('statReceived', _fbData.length);
  setText('statQueue',    qN);
  setText('queueCount',   qN);
  setText('pendingCount', qN);
  setText('givenCount',   _myRevData.length);
  setText('receivedCount',_fbData.length);

  const pendingDot = $('pendingDot');
  if (pendingDot) pendingDot.style.display = qN > 0 ? 'block' : 'none';

  const cText = $('queueCountText');
  if (cText) cText.textContent = qN + " ta baholash kutmoqda";

  if (_fbData.length > 0) {
    const avg = _fbData.reduce((s, r) => s + (r.star_rating || 0), 0) / _fbData.length;
    setText('statRating', avg.toFixed(1));
    setText('receivedAvg', `⭐ ${avg.toFixed(1)} / 5.0 o'rtacha`);
  } else {
    setText('statRating', '—');
  }

  if (_myRevData.length > 0) {
    const avg = _myRevData.reduce((s, r) => s + (r.star_rating || 0), 0) / _myRevData.length;
    setText('givenAvg', `O'rtacha bergan: ${avg.toFixed(1)}/5`);
  }
}

function renderQueue() {
  const el = $('reviewQueue');
  el.innerHTML = '';
  if (!_queueData.length) {
    el.innerHTML = '<div style="text-align:center;padding:2rem;color:var(--muted)">🎉 Hozircha baholash navbati bo\'sh!</div>';
    return;
  }
  _queueData.forEach((ts, i) => {
    const init = (ts.topic_title || 'M')[0].toUpperCase();
    const div = document.createElement('div');
    div.className = 'review-card';
    div.innerHTML = `
      <div class="rc-header">
        <div class="rc-student">
          <div class="rc-avatar" style="background:${avatarColors(i)}">${init}</div>
          <div>
            <div class="rc-name">Mavzu ${ts.topic_number || ''}: ${ts.topic_title || "Noma'lum mavzu"}</div>
            <div class="rc-task">${levelLabel(ts.level)} daraja • Baholashga tayyor</div>
          </div>
        </div>
        <div class="rc-badges"><span class="badge-pill bp-new">Yangi</span></div>
      </div>
      <div style="background:#0d1117;border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:.8rem 1rem;font-size:.82rem;color:var(--muted);margin-bottom:.8rem">
        📊 Talaba ushbu mavzu bo'yicha barcha topshiriqlarni yakunlagan. Mezon bo'yicha baholang.
      </div>
      <div class="rc-footer">
        <span class="rc-meta">📚 Mavzu ${ts.topic_number || ''} • C#</span>
        <div class="rc-actions">
          <button class="rc-btn rc-btn-review" onclick="openReview(${ts.id})">🔍 Baholash</button>
        </div>
      </div>`;
    el.appendChild(div);
  });
}

function renderMyReviews() {
  const el = $('myReviews');
  el.innerHTML = '';
  if (!_myRevData.length) {
    el.innerHTML = '<div style="text-align:center;padding:2rem;color:var(--muted)">Hali review bermadingiz</div>';
    return;
  }
  _myRevData.forEach(r => {
    const stars = r.star_rating || 0;
    const starsHtml = '⭐'.repeat(stars) + '<span class="star-empty">' + '⭐'.repeat(5 - stars) + '</span>';
    const chips = ['ko_score','fa_score','ad_score','kr_score','re_score']
      .map(k => `<span class="score-chip">${k.replace('_score','').toUpperCase()}: ${r[k] || 0}</span>`).join('');
    const reviewee = r.reviewee ? (r.reviewee.full_name || r.reviewee.username || 'Talaba') : 'Talaba';
    el.innerHTML += `<div class="mr-item">
      <div class="mr-header">
        <div>
          <div class="mr-title">Mavzu ${r.topic_number || ''}: ${r.topic_title || ''} — ${reviewee}</div>
          <div class="mr-meta">${fmtDate(r.created_at)}</div>
        </div>
      </div>
      <div class="star-row">${starsHtml}</div>
      <div class="score-chips">${chips}</div>
      <div class="mr-comment" style="margin-top:.5rem">"${r.comment || ''}"</div>
    </div>`;
  });
}

function renderReceived() {
  const el = $('feedbackList');
  el.innerHTML = '';
  if (!_fbData.length) {
    el.innerHTML = '<div style="text-align:center;padding:2rem;color:var(--muted)">Hali peer review olmadingiz</div>';
    return;
  }
  _fbData.forEach(f => {
    const reviewer = f.reviewer ? (f.reviewer.full_name || f.reviewer.username || 'Reviewer') : 'Reviewer';
    const init = reviewer[0].toUpperCase();
    const scoreItems = ['ko_score','fa_score','ad_score','kr_score','re_score']
      .map(k => `<div class="fb-score-item"><div class="fb-score-label">${k.replace('_score','').toUpperCase()}</div><div class="fb-score-val" style="color:#a78bfa">${f[k] || 0}</div></div>`).join('');
    el.innerHTML += `<div class="fb-item">
      <div class="fb-header">
        <div style="width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,#6c63ff,#ff6584);display:flex;align-items:center;justify-content:center;font-size:.75rem;font-weight:700">${init}</div>
        <div class="fb-reviewer">${reviewer}</div>
        <div class="fb-date">${fmtDate(f.created_at)}</div>
      </div>
      <div class="fb-topic">📚 Mavzu ${f.topic_number || ''}: ${f.topic_title || ''}</div>
      <div class="fb-scores">${scoreItems}</div>
      <div class="fb-comment">"${f.comment || ''}"</div>
    </div>`;
  });
}

function renderLeaderboard() {
  const el = $('reviewerList');
  el.innerHTML = '';
  if (!_lbData.length) {
    el.innerHTML = '<div style="text-align:center;padding:2rem;color:var(--muted)">Hali leaderboard mavjud emas</div>';
    return;
  }
  let myId = null;
  try { const u = JSON.parse(localStorage.getItem('cw_user') || '{}'); myId = u.id; } catch {}

  const medalBgs = [
    'linear-gradient(135deg,#f97316,#ffd700)',
    'linear-gradient(135deg,#c0c0c0,#e8e8e8)',
    'linear-gradient(135deg,#cd7f32,#b8860b)',
  ];

  _lbData.forEach((item, idx) => {
    const user  = item.user || {};
    const name  = user.full_name || user.username || 'Talaba';
    const init  = name[0].toUpperCase();
    const rank  = item.rank || (idx + 1);
    const isMe  = myId && user.id === myId;
    const posClass = rank===1?'gold': rank===2?'silver': rank===3?'bronze':'';
    const posIcon  = rank===1?'🥇':  rank===2?'🥈':    rank===3?'🥉': rank;
    const bg = medalBgs[rank - 1] || avatarColors(idx);

    el.innerHTML += `<div class="rv-item ${isMe ? 'highlight' : ''}">
      <span class="rv-pos ${posClass}">${posIcon}</span>
      <div class="rv-av" style="background:${bg}">${init}</div>
      <div class="rv-info">
        <div class="rv-name">${name}${isMe ? ' <span style="font-size:.65rem;color:var(--accent)">(men)</span>' : ''}</div>
        <div class="rv-meta">${item.review_count || 0} ta review</div>
      </div>
      <span class="rv-pts">${item.review_count || 0} ta</span>
    </div>`;
  });
}

function buildCriteriaGrid() {
  const grid = $('criteriaGrid');
  grid.innerHTML = '';
  Object.keys(scores).forEach(k => scores[k] = 0);
  criteria.forEach(c => {
    const div = document.createElement('div');
    div.className = 'criterion-row';
    div.innerHTML = `<div class="cr-label">${c.name} <span id="val-${c.key}">0/${c.max}</span></div>
      <input type="range" class="cr-slider" min="0" max="${c.max}" value="0" oninput="updateScore('${c.key}',this.value,${c.max})"/>`;
    grid.appendChild(div);
  });
}

function updateScore(key, val, max) {
  scores[key] = parseInt(val);
  $('val-' + key).textContent = val + '/' + max;
  const total = Object.values(scores).reduce((a, b) => a + b, 0);
  $('totalScore').textContent = total + ' / 90';
}

function setStars(n) {
  selectedStars = n;
  document.querySelectorAll('.star-picker .sp-star').forEach((s, i) => {
    s.textContent = i < n ? '⭐' : '☆';
  });
}

function openReview(topicScoreId) {
  activeTopicScoreId = topicScoreId;
  const ts = _queueData.find(t => t.id === topicScoreId);
  if (!ts) return;

  $('reviewModalMeta').textContent = `Mavzu ${ts.topic_number || ''}: ${ts.topic_title || ''} • ${levelLabel(ts.level)} daraja`;

  const diffView = document.querySelector('.diff-view');
  if (diffView) diffView.style.display = 'none';

  buildCriteriaGrid();
  setStars(3);
  $('reviewComment').value = '';
  openModal('reviewModal');
}

async function submitReview() {
  const comment = $('reviewComment').value;
  if (!comment.trim()) { alert("Iltimos, izoh yozing!"); return; }
  if (!selectedStars)  { alert("Iltimos, yulduz reytingini tanlang!"); return; }
  if (!activeTopicScoreId) return;

  const btn = document.querySelector('#reviewModal .btn-primary');
  try {
    if (btn) { btn.disabled = true; btn.textContent = 'Yuborilmoqda...'; }

    await api.submitPeerReview({
      topic_score: activeTopicScoreId,
      ko_score:    scores.ko_score,
      fa_score:    scores.fa_score,
      ad_score:    scores.ad_score,
      kr_score:    scores.kr_score,
      re_score:    scores.re_score,
      comment,
      star_rating: selectedStars,
    });

    _queueData = _queueData.filter(t => t.id !== activeTopicScoreId);
    renderQueue();
    renderStats();

    closeModal('reviewModal');
    setTimeout(() => openModal('successModal'), 200);

    api.myReviews('given').then(data => {
      _myRevData = Array.isArray(data) ? data : (data.results || []);
      renderMyReviews();
      renderStats();
    }).catch(() => {});

  } catch(e) {
    alert('Xatolik: ' + (e.message || 'Noma\'lum xato'));
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = '✅ Yuborish'; }
  }
}

function switchTab(id) {
  document.querySelectorAll('.tab-btn').forEach((b, i) => {
    const tabs = ['queue','myreviews','received','leaderboard'];
    b.classList.toggle('active', tabs[i] === id);
  });
  document.querySelectorAll('.tab-content').forEach(t => {
    t.classList.toggle('active', t.id === 'tab-' + id);
  });
}

function openModal(id)  { $(id).classList.add('open'); }
function closeModal(id) { $(id).classList.remove('open'); }
function openGuide()    { openModal('guideModal'); }
document.querySelectorAll('.modal-overlay').forEach(m =>
  m.addEventListener('click', function(e) { if (e.target === this) this.classList.remove('open'); }));
