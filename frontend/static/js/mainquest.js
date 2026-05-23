if (!Auth.requireAuth()) throw 0;

let MODULES = {};
let TOPICS = {};
let activeTestObj = null;

const KO_MAP = {beginner:5, intermediate:7, advanced:8};
const LEVEL_SUFFIX = {beginner:'b', intermediate:'o', advanced:'y'};
const LEVEL_NAME   = {beginner:"Boshlang'ich", intermediate:"O'rta", advanced:"Yuqori"};

let curModule  = 1;
let curTopic   = null;
let curDaraja  = 'beginner';
let testQ = [], testAns = {}, testIdx = 0, testLevel = 'beginner';

function switchModule(num, el) {
  curModule = num;
  document.querySelectorAll('.mod-tab').forEach(t => t.classList.remove('active'));
  if (el) el.classList.add('active');
  const m = MODULES[num] || {};
  document.getElementById('modIcon').textContent  = m.icon  || '📗';
  document.getElementById('modTitle').textContent = m.title || '';
  document.getElementById('modDesc').textContent  = m.desc  || '';
  renderTopics();
}

function renderTopics() {
  const grid   = document.getElementById('topicsGrid');
  const topics = TOPICS[curModule] || [];
  let done = 0;

  grid.innerHTML = topics.map(t => {
    const total = t.score.mo + t.score.ko + t.score.fa + t.score.ad + t.score.kr + t.score.re;
    const allDone = t.bPass && t.oPass && t.yPass;
    if (allDone) done++;

    const [stLabel, stCls] = allDone ? ['Tugatildi','st-done'] :
                             total > 0 ? ['Davomda','st-prog'] : ['Ochiq','st-open'];

    const diffLabel = {easy:'Oson', medium:"O'rta", hard:'Qiyin'}[t.diff] || t.diff;

    return `<div class="topic-card" onclick="openDetail(${t.id})">
      <div class="tc-top">
        <div class="tc-num">Mavzu ${t.num}</div>
        <div class="tc-status ${stCls}">${stLabel}</div>
      </div>
      <div class="tc-title">${t.title}</div>
      <div class="tc-meta">
        <span class="tc-tag ${t.diff}">${diffLabel}</span>
        <span class="tc-tag">📺 ${countContent(t)} kontent</span>
        <span class="tc-tag">📝 ${countTests(t)}/3 test</span>
      </div>
      <div class="level-pills">
        <span class="lp b">${t.bPass?'✓':''} Boshlang'ich</span>
        <span class="lp o ${t.bPass?'':'locked'}">${t.oPass?'✓':''} O'rta</span>
        <span class="lp y ${t.oPass?'':'locked'}">${t.yPass?'✓':''} Yuqori</span>
      </div>
      <div class="prog-row">
        <div class="prog-label"><span>Ball</span><span class="pval">${total}/100</span></div>
        <div class="prog-bar"><div class="prog-fill" style="width:${total}%"></div></div>
      </div>
    </div>`;
  }).join('');

  document.getElementById('modPct').textContent =
    topics.length ? Math.round(done / topics.length * 100) + '%' : '0%';
}

function countContent(t) {
  return ['beginner','intermediate','advanced'].filter(lv =>
    t.contents[lv]?.video || t.contents[lv]?.text?.length > 30
  ).length;
}

function countTests(t) {
  return (t.bPass ? 1 : 0) + (t.oPass ? 1 : 0) + (t.yPass ? 1 : 0);
}

function closeDetail() {
  document.getElementById('detailOverlay').classList.remove('open');
  document.getElementById('detailPanel').classList.remove('open');
}

function renderDarajaTabs() {
  const levels  = ['beginner','intermediate','advanced'];
  const ids     = ['dtabB','dtabO','dtabY'];
  const clsMap  = ['active-b','active-o','active-y'];
  const locked  = [false, !curTopic.bPass, !curTopic.oPass];

  levels.forEach((lv, i) => {
    const btn = document.getElementById(ids[i]);
    btn.className = 'daraja-tab';

    if (locked[i]) {
      btn.classList.add('locked-tab');
      btn.onclick = () => showToast('🔒 Bu darajani ochish uchun avvalgi daraja testini topshiring!');
    } else {
      btn.onclick = () => switchDaraja(lv);
      if (lv === curDaraja) btn.classList.add(clsMap[i]);
    }
  });
}

function switchDaraja(level) {
  if (!curTopic) return;
  const locked = {intermediate: !curTopic.bPass, advanced: !curTopic.oPass};
  if (locked[level]) { showToast('🔒 Bu daraja hali qulflanmagan!'); return; }

  curDaraja = level;
  renderDarajaTabs();

  ['beginner','intermediate','advanced'].forEach(lv => {
    document.getElementById(`lc-${lv}`).classList.toggle('show', lv === level);
  });
}

function loadLevelContent() {
  const levels = ['beginner','intermediate','advanced'];
  const sfx    = {beginner:'b', intermediate:'o', advanced:'y'};

  levels.forEach(lv => {
    const c = curTopic.contents[lv] || {};
    const p = curTopic.lvProgress[lv] || {};
    const s = sfx[lv];

    const wrap = document.getElementById(`vidWrap-${s}`);
    if (wrap) {
      const ytId = getYoutubeId(c.video);
      if (ytId) {
        wrap.innerHTML = `<iframe
          src="https://www.youtube.com/embed/${ytId}"
          frameborder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen
          style="width:100%;height:100%;border-radius:10px;"></iframe>`;
        wrap.style.cursor = 'default';
        wrap.onclick = null;
      } else {
        wrap.innerHTML = `<div class="play-btn">▶</div><p>${LEVEL_NAME[lv]} daraja video tez kunda</p>`;
        wrap.style.cursor = 'default';
        wrap.onclick = null;
      }
    }

    const lect = document.getElementById(`lecture-${s}`);
    if (lect) lect.innerHTML = c.text || '<p style="color:var(--muted)">Matn tez kunda qo\'shiladi.</p>';

    applyVideoState(s, p.vid);
    applyTextState(s, p.txt);
  });

  levels.forEach(lv => {
    document.getElementById(`lc-${lv}`).classList.toggle('show', lv === curDaraja);
  });
}

function applyVideoState(s, done) {
  const wrap = document.getElementById(`vidWrap-${s}`);
  const btn  = document.getElementById(`vidBtn-${s}`);
  const tag  = document.getElementById(`vid-done-${s}`);
  if (done) {
    wrap?.classList.add('watched');
    if (btn) { btn.textContent = '✅ Ko\'rildi'; btn.classList.add('done'); }
    if (tag) tag.style.display = '';
  } else {
    wrap?.classList.remove('watched');
    if (btn) { btn.textContent = '✅ Videoni ko\'rdim'; btn.classList.remove('done'); }
    if (tag) tag.style.display = 'none';
  }
}

function applyTextState(s, done) {
  const btn = document.getElementById(`txtBtn-${s}`);
  const tag = document.getElementById(`txt-done-${s}`);
  if (done) {
    if (btn) { btn.textContent = "✅ O'qildi"; btn.classList.add('done'); }
    if (tag) tag.style.display = '';
  } else {
    if (btn) { btn.textContent = "✅ Matnni o'qidim"; btn.classList.remove('done'); }
    if (tag) tag.style.display = 'none';
  }
}

function getYoutubeId(url) {
  if (!url) return null;
  const m = url.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/|v\/))([\w-]{11})/);
  return m ? m[1] : null;
}

function watchVideo(level) {
  showToast('🎬 Video tez kunda qo\'shiladi!');
}

async function markVideo(level) {
  if (!curTopic) return;
  try {
    await api.updateProgress(curTopic.id, { level, video_watched: true });
    curTopic.lvProgress[level].vid = true;
    applyVideoState(LEVEL_SUFFIX[level], true);
    checkAndAwardAD(level);
    showToast('🎬 Video ko\'rildi!');
  } catch { showToast('❌ Xatolik yuz berdi'); }
}

async function markText(level) {
  if (!curTopic) return;
  try {
    await api.updateProgress(curTopic.id, { level, text_read: true });
    curTopic.lvProgress[level].txt = true;
    applyTextState(LEVEL_SUFFIX[level], true);
    checkAndAwardAD(level);
    renderAllTestCTAs();
    showToast('📖 Matn o\'qildi!');
  } catch { showToast('❌ Xatolik yuz berdi'); }
}

function checkAndAwardAD(level) {
  const p = curTopic.lvProgress[level];
  if (p.vid && p.txt && !p.adDone) {
    p.adDone = true;
    curTopic.score.ad = Math.min(15, curTopic.score.ad + 5);
    renderScoreSummary();
    renderTopics();
    showToast(`🌟 ${LEVEL_NAME[level]} daraja o'qildi! +5 AD ball`);
  }
}

function renderAllTestCTAs() {
  ['beginner','intermediate','advanced'].forEach(lv => renderTestCTA(lv));
}

function renderTestCTA(level) {
  const area   = document.getElementById(`testCta-${level}`);
  if (!area || !curTopic) return;
  const cls    = {beginner:'b', intermediate:'o', advanced:'y'}[level];
  const passed = {beginner: curTopic.bPass, intermediate: curTopic.oPass, advanced: curTopic.yPass}[level];
  const locked = {intermediate: !curTopic.bPass, advanced: !curTopic.oPass}[level] || false;
  const p      = curTopic.lvProgress[level] || {};
  const ready  = p.vid && p.txt;

  let btnHtml = '';
  if (passed) {
    btnHtml = `<span class="test-done-badge">✓ O'tildi</span>`;
  } else if (locked) {
    btnHtml = `<button class="test-btn ${cls}" disabled>🔒 Qulflangan</button>`;
  } else if (!ready) {
    btnHtml = `<button class="test-btn ${cls}" disabled title="Avval video va matnni tugatg">📺 Avval kontentni tugatg</button>`;
  } else {
    btnHtml = `<button class="test-btn ${cls}" onclick="startTest('${level}')">📝 Test boshlash →</button>`;
  }

  area.innerHTML = `<div class="test-cta ${cls}">
    <div class="tc-left">
      <h4>📝 ${LEVEL_NAME[level]} daraja testi</h4>
      <p>10 savol · O'tish: 7/10 · +${KO_MAP[level]} KO ball, +5 AD ball</p>
    </div>
    ${btnHtml}
  </div>`;
}

function renderScoreSummary() {
  if (!curTopic) return;
  const s = curTopic.score;
  const items = [
    {k:'MO', v:s.mo, max:10,  color:'#a78bfa'},
    {k:'KO', v:s.ko, max:20,  color:'#6c63ff'},
    {k:'FA', v:s.fa, max:30,  color:'#43e97b'},
    {k:'AD', v:s.ad, max:15,  color:'#ff9800'},
    {k:'KR', v:s.kr, max:15,  color:'#ff6584'},
    {k:'RE', v:s.re, max:10,  color:'#38f9d7'},
  ];
  const labels = {MO:'Motivatsion',KO:'Kognitiv',FA:'Faoliyat',AD:'Adaptiv',KR:'Kreativ',RE:'Reflektiv'};
  const total  = items.reduce((a,x) => a+x.v, 0);

  document.getElementById('scoreGrid').innerHTML =
    items.map(x => `<div class="score-cell">
      <div class="sc-label">${labels[x.k]}</div>
      <div class="sc-val" style="color:${x.color}">${x.v}/${x.max}</div>
      <div class="sc-bar"><div class="sc-fill" style="width:${Math.round(x.v/x.max*100)}%;background:${x.color}"></div></div>
    </div>`).join('') +
    `<div class="score-total">
      <div style="font-size:.65rem;color:var(--muted);margin-bottom:.2rem">JAMI BALL</div>
      <div style="font-size:1.5rem;font-weight:900;background:linear-gradient(135deg,#6c63ff,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent">${total}/100</div>
    </div>`;
}

async function startTest(level) {
  testLevel = level;
  testAns   = {};
  testIdx   = 0;

  try {
    const tests = await api.topicTests(curTopic.id);
    const test  = tests.find(t => t.level === level);
    if (!test) { showToast('Test topilmadi'); return; }

    activeTestObj = test;
    const qs = test.questions || [];
    testQ = qs.map(q => ({
      id: q.id,
      q:  q.question,
      options: q.options,
      c:  q.correct_answer,
    }));

    document.getElementById('testModalTitle').textContent = `${LEVEL_NAME[level]} Daraja Testi`;
    document.getElementById('testModalSub').textContent   = `${testQ.length} savol · O'tish: ${test.pass_score}/${testQ.length} to'g'ri javob`;
    renderTestNav(); renderQuestion();
    document.getElementById('testModal').classList.add('open');
  } catch (err) {
    showToast('❌ Test yuklanmadi: ' + err.message);
  }
}

function renderTestNav() {
  document.getElementById('testNav').innerHTML = testQ.map((q,i) =>
    `<button class="test-nav-btn ${testAns[q.id]!==undefined?'answered':''} ${i===testIdx?'current':''}"
      onclick="goQ(${i})">${i+1}</button>`
  ).join('');
}

function renderQuestion() {
  const q   = testQ[testIdx];
  const pct = (testIdx+1) / testQ.length * 100;
  document.getElementById('testProgFill').style.width = pct+'%';
  document.getElementById('questionArea').innerHTML = `
    <div class="question-block">
      <div class="q-num">Savol ${testIdx+1} / ${testQ.length}</div>
      <div class="q-text">${q.q}</div>
      <div class="q-options">
        ${q.options.map((opt,i) => `
          <div class="q-option ${testAns[q.id]===i?'selected':''}" onclick="pickAns(${q.id},${i})">
            <div class="opt-letter">${'ABCD'[i]}</div>${opt}
          </div>`).join('')}
      </div>
    </div>`;
  document.getElementById('prevBtn').disabled    = testIdx === 0;
  document.getElementById('nextBtn').textContent = testIdx === testQ.length-1 ? 'Yakunlash ✓' : 'Keyingi →';
  renderTestNav();
}

function pickAns(qId, i) { testAns[qId] = i; renderQuestion(); }
function goQ(i)           { testIdx = i; renderQuestion(); }
function prevQuestion()   { if (testIdx > 0) { testIdx--; renderQuestion(); } }
function nextOrSubmit()   { if (testIdx < testQ.length-1) { testIdx++; renderQuestion(); } else submitTest(); }

async function submitTest() {
  const unanswered = testQ.length - Object.keys(testAns).length;
  if (unanswered > 0 && !confirm(`${unanswered} ta savol javobsiz. Yakunlashni xohlaysizmi?`)) return;

  const answers = {};
  testQ.forEach(q => { if (testAns[q.id] !== undefined) answers[q.id] = testAns[q.id]; });

  try {
    const res = await api.submitTest(curTopic.id, activeTestObj.id, answers);
    const score  = res.score ?? 0;
    const passed = res.passed ?? false;
    const ko     = passed ? KO_MAP[testLevel] : 0;

    document.getElementById('resultRing').className    = `result-score-ring ${passed?'pass':'fail'}`;
    document.getElementById('resultScore').textContent  = score;
    document.getElementById('resultTitle').textContent  = passed ? '🎉 Tabriklaymiz!' : '😔 Muvaffaqiyatsiz';
    document.getElementById('resultMsg').textContent    = passed
      ? `${LEVEL_NAME[testLevel]} daraja testi ${score}/${testQ.length} natija bilan o'tildi!`
      : `${score}/${testQ.length} to'g'ri javob. O'tish uchun kamida ${activeTestObj.pass_score} ta to'g'ri javob kerak.`;
    document.getElementById('rewardRow').innerHTML = passed
      ? `<div class="reward-pill ko">+${ko} KO ball</div><div class="reward-pill ad">+5 AD ball</div>` : '';

    if (passed) {
      if (testLevel==='beginner')     curTopic.bPass = true;
      if (testLevel==='intermediate') curTopic.oPass = true;
      if (testLevel==='advanced')     curTopic.yPass = true;
      curTopic.score.ko = Math.min(20, curTopic.score.ko + ko);
      curTopic.score.ad = Math.min(15, curTopic.score.ad + 5);
    }

    closeTestModal();
    document.getElementById('resultModal').classList.add('open');
  } catch (err) {
    showToast('❌ Test yuborishda xatolik: ' + err.message);
  }
}

function closeTestModal() { document.getElementById('testModal').classList.remove('open'); }

function closeResult() {
  document.getElementById('resultModal').classList.remove('open');
  renderDarajaTabs();
  renderAllTestCTAs();
  renderScoreSummary();
  renderTopics();
}

function retryTest() {
  document.getElementById('resultModal').classList.remove('open');
  setTimeout(() => startTest(testLevel), 200);
}

function showToast(msg) {
  const t = document.createElement('div');
  t.style.cssText='position:fixed;bottom:1.5rem;right:1.5rem;background:#1a1f3a;border:1px solid rgba(108,99,255,0.4);border-radius:14px;padding:.75rem 1.2rem;font-size:.85rem;font-weight:600;z-index:999;animation:fi .3s ease;box-shadow:0 8px 30px rgba(0,0,0,.3)';
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 2600);
}
const _s = document.createElement('style');
_s.textContent = '@keyframes fi{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}';
document.head.appendChild(_s);

async function openDetail(topicId) {
  const all = Object.values(TOPICS).flat();
  curTopic = all.find(t => t.id === topicId);
  if (!curTopic) return;

  document.getElementById('dpTitle').textContent = `T${curTopic.num}: ${curTopic.title}`;
  document.getElementById('dpSub').textContent   = `Modul ${curModule} · 3 daraja · video + maruza + test`;

  curDaraja = !curTopic.bPass ? 'beginner' :
              !curTopic.oPass ? 'intermediate' : 'advanced';

  try {
    const [contents, progressList] = await Promise.all([
      api.topicContents(topicId),
      api.myProgress(topicId),
    ]);

    contents.forEach(c => {
      curTopic.contents[c.level] = { video: c.video_url, text: c.lecture_text };
    });
    progressList.forEach(p => {
      curTopic.lvProgress[p.level] = {
        vid: p.video_watched, txt: p.text_read, adDone: p.ad_awarded
      };
    });
  } catch {}

  loadLevelContent();
  renderDarajaTabs();
  renderAllTestCTAs();
  renderScoreSummary();

  document.getElementById('detailOverlay').classList.add('open');
  document.getElementById('detailPanel').classList.add('open');
}

async function initPage() {
  Auth.fillUserUI();
  try {
    const [modules, topics, scores] = await Promise.all([
      api.modules(),
      api.topics(),
      api.scores(),
    ]);

    const MOD_ICONS = ['📗','📘','📙','📕','📔','📒','📓','📃','📑'];
    modules.forEach((m, i) => {
      MODULES[m.number] = {
        id: m.id, icon: MOD_ICONS[i % MOD_ICONS.length],
        title: `Modul ${m.number}: ${m.title}`, desc: m.description || '',
      };
    });

    const scoreMap = {};
    scores.forEach(s => { scoreMap[s.topic] = s; });

    TOPICS = {};
    topics.forEach(t => {
      const mod = t.module?.number || 1;
      if (!TOPICS[mod]) TOPICS[mod] = [];
      const sc = scoreMap[t.id] || {};
      TOPICS[mod].push({
        id: t.id, num: t.number, title: t.title, diff: t.difficulty,
        bPass: !!sc.beginner_test_passed,
        oPass: !!sc.intermediate_test_passed,
        yPass: !!sc.advanced_test_passed,
        lvProgress: {
          beginner:     {vid:false, txt:false, adDone:false},
          intermediate: {vid:false, txt:false, adDone:false},
          advanced:     {vid:false, txt:false, adDone:false},
        },
        score: {
          mo:sc.mo_score||0, ko:sc.ko_score||0, fa:sc.fa_score||0,
          ad:sc.ad_score||0, kr:sc.kr_score||0, re:sc.re_score||0,
        },
        contents: {
          beginner:     {video:'', text:''},
          intermediate: {video:'', text:''},
          advanced:     {video:'', text:''},
        },
      });
    });

    const tabsEl = document.querySelector('.mod-tabs');
    if (tabsEl) {
      tabsEl.innerHTML = modules.map((m, i) =>
        `<div class="mod-tab ${i===0?'active':''}" onclick="switchModule(${m.number}, this)">
          Modul ${m.number}
        </div>`
      ).join('');
    }

    if (modules.length) switchModule(modules[0].number, null);
  } catch (err) {
    console.error('Sahifa yuklanmadi:', err);
  }
}

initPage();
