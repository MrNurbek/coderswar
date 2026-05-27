/* ═══════════════════════════════════════════════
   Coders War — API Wrapper
   fetch() + JWT auto-refresh + error handling
   ═══════════════════════════════════════════════ */

const api = (() => {

  async function request(method, path, body = null, _retry = true) {
    const headers = {};
    const token = Auth.getAccess();
    if (token) headers['Authorization'] = `Bearer ${token}`;
    if (body)  headers['Content-Type']  = 'application/json';

    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);

    let res;
    try {
      res = await fetch(`${API_BASE}${path}`, opts);
    } catch {
      throw new Error('Serverga ulanib bo\'lmadi. Internetni tekshiring.');
    }

    // 401 — token eskirgan, yangilash
    if (res.status === 401 && _retry) {
      const ok = await Auth.refreshToken();
      if (ok) return request(method, path, body, false);
      Auth.logout();
      return null;
    }

    return res;
  }

  async function json(method, path, body = null) {
    const res = await request(method, path, body);
    if (!res) return null;
    if (!res.ok) {
      let msg = `${res.status}`;
      try { const d = await res.json(); msg = d.detail || d.message || JSON.stringify(d); }
      catch {}
      throw new Error(msg);
    }
    if (res.status === 204) return null;
    return res.json();
  }

  // Avatar va boshqa fayl upload uchun (multipart/form-data)
  async function uploadFile(path, formData) {
    const headers = {};
    const token = Auth.getAccess();
    if (token) headers['Authorization'] = `Bearer ${token}`;
    // Content-Type ni o'rnatmaymiz — browser o'zi boundary qo'shadi

    let res;
    try {
      res = await fetch(`${API_BASE}${path}`, { method: 'PATCH', headers, body: formData });
    } catch {
      throw new Error('Serverga ulanib bo\'lmadi.');
    }
    if (!res.ok) {
      let msg = `${res.status}`;
      try { const d = await res.json(); msg = d.detail || d.message || JSON.stringify(d); }
      catch {}
      throw new Error(msg);
    }
    return res.json();
  }

  return {
    // Asosiy metodlar
    get:    (path)        => json('GET',    path),
    post:   (path, body)  => json('POST',   path, body),
    put:    (path, body)  => json('PUT',    path, body),
    patch:  (path, body)  => json('PATCH',  path, body),
    delete: (path)        => json('DELETE', path),

    // Raw response (kerak bo'lganda)
    raw: request,

    // ── Auth ──────────────────────────────────────────────────
    me:             ()       => api.get('/auth/me/'),
    register:       (data)   => api.post('/auth/register/', data),
    verifyOtp:      (data)   => api.post('/auth/verify-otp/', data),
    resendOtp:      (email)  => api.post('/auth/resend-otp/', { email }),

    // Parol tiklash
    forgotPassword: (email)  => api.post('/auth/forgot-password/', { email }),
    resetPassword:  (data)   => api.post('/auth/reset-password/', data),

    // Avatar upload (multipart/form-data)
    uploadAvatar: (file) => {
      const fd = new FormData();
      fd.append('avatar', file);
      return uploadFile('/auth/me/avatar/', fd);
    },

    // Admin: foydalanuvchi bloklash/blokdan chiqarish
    blockUser:   (id) => api.post(`/auth/users/${id}/block/`,   {}),
    unblockUser: (id) => api.post(`/auth/users/${id}/unblock/`, {}),

    // ── Courses ───────────────────────────────────────────────
    modules:       ()        => api.get('/courses/modules/'),
    topics:        (params)  => api.get('/courses/topics/' + (params ? '?' + new URLSearchParams(params) : '')),
    topic:         (id)      => api.get(`/courses/topics/${id}/`),
    topicContents: (id)      => api.get(`/courses/topics/${id}/contents/`),
    topicTests:    (id)      => api.get(`/courses/topics/${id}/tests/`),
    myProgress:    (id)      => api.get(`/courses/topics/${id}/my-progress/`),
    updateProgress:(id, d)   => api.patch(`/courses/topics/${id}/my-progress/`, d),
    submitTest:    (topicId, testId, answers) =>
      api.post(`/courses/topics/${topicId}/tests/${testId}/submit/`, { answers }),
    tasks:         (params)  => api.get('/courses/tasks/' + (params ? '?' + new URLSearchParams(params) : '')),
    scores:        ()        => api.get('/courses/scores/'),
    topicScore:    (topicId) => api.get(`/courses/scores/?topic=${topicId}`),
    studentScores: (studentId) => api.get(`/courses/scores/?student=${studentId}`),
    giveMoScore:         (scoreId, moScore) => api.patch(`/courses/scores/${scoreId}/give-mo/`,         { mo_score: moScore }),
    giveFaProjectScore:  (scoreId, score)   => api.patch(`/courses/scores/${scoreId}/give-fa-project/`, { fa_project_score: score }),
    giveRePeerScore:     (scoreId, score)   => api.patch(`/courses/scores/${scoreId}/give-re-peer/`,    { re_peer_score: score }),
    submitCode:    (data)    => api.post('/courses/submissions/', data),
    submission:    (id)      => api.get(`/courses/submissions/${id}/`),
    reflections:   ()        => api.get('/courses/reflections/'),
    saveReflection:(data)    => api.post('/courses/reflections/', data),

    // ── O'qituvchi: kontent boshqaruvi ───────────────────────
    contentCreate:    (topicId, data)         => api.post(`/courses/topics/${topicId}/contents/`, data),
    contentUpdate:    (topicId, cid, data)    => api.patch(`/courses/topics/${topicId}/contents/${cid}/`, data),
    testCreate:       (topicId, data)         => api.post(`/courses/topics/${topicId}/tests/`, data),
    testUpdate:       (topicId, tid, data)    => api.patch(`/courses/topics/${topicId}/tests/${tid}/`, data),
    testSetQuestions: (topicId, tid, qs)      => api.post(`/courses/topics/${topicId}/tests/${tid}/set-questions/`, { questions: qs }),
    taskCreate:       (data)                  => api.post('/courses/tasks/', data),
    taskUpdate:       (id, data)              => api.patch(`/courses/tasks/${id}/`, data),
    taskDelete:       (id)                    => api.delete(`/courses/tasks/${id}/`),
    topicTasksList:   (topicId, level)        => api.get(`/courses/tasks/?topic=${topicId}&level=${level}&ordering=order`),

    // Baholash navbati (o'qituvchi uchun)
    pendingGrades: () => api.get('/courses/pending-grades/'),

    // AI hisobot (o'qituvchi uchun)
    aiReport: (studentId, topicId) => {
      const p = new URLSearchParams({ student_id: studentId });
      if (topicId) p.append('topic_id', topicId);
      return api.get(`/courses/ai-report/?${p}`);
    },

    // ── Game ──────────────────────────────────────────────────
    leaderboard:  ()       => api.get('/game/leaderboard/'),
    myBadges:     ()       => api.get('/game/badges/mine/'),
    allBadges:    ()       => api.get('/game/badges/'),
    clans:        ()       => api.get('/game/clans/'),
    clanLeaderboard: ()  => api.get('/game/leaderboard/clans/'),
    clan:         (id)     => api.get(`/game/clans/${id}/`),
    createClan:   (data)   => api.post('/game/clans/', data),
    joinClan:     (id)     => api.post(`/game/clans/${id}/join/`, {}),
    leaveClan:    (id)     => api.post(`/game/clans/${id}/leave/`, {}),
    applyClan:    (id, msg) => api.post(`/game/clans/${id}/apply/`, { message: msg || '' }),
    myApplication:(id)     => api.get(`/game/clans/${id}/my-application/`),
    clanApplications:(id)  => api.get(`/game/clans/${id}/applications/`),
    approveApplication:(clanId, appId) => api.post(`/game/clans/${clanId}/applications/${appId}/approve/`, {}),
    rejectApplication: (clanId, appId) => api.post(`/game/clans/${clanId}/applications/${appId}/reject/`, {}),
    clanChat:     (id)     => api.get(`/game/clans/${id}/chat/`),
    sendClanMsg:  (id, message) => api.post(`/game/clans/${id}/chat/send/`, { message }),
    duels:        ()       => api.get('/game/duels/'),
    createDuel:   (data)   => api.post('/game/duels/', data),
    joinDuel:     (id)     => api.post(`/game/duels/${id}/join/`, {}),
    cancelDuel:   (id)     => api.post(`/game/duels/${id}/cancel/`, {}),

    // Klan urushlari
    clanWars:        (params) => api.get('/game/clan-wars/' + (params ? '?' + new URLSearchParams(params) : '')),
    createClanWar:   (data)   => api.post('/game/clan-wars/', data),
    acceptClanWar:   (id)     => api.post(`/game/clan-wars/${id}/accept/`, {}),
    finishClanWar:   (id, data) => api.post(`/game/clan-wars/${id}/finish/`, data),
    cancelClanWar:   (id)     => api.post(`/game/clan-wars/${id}/cancel/`, {}),

    // Inventory (qurol-aslahalar)
    inventory:    ()            => api.get('/game/inventory/'),
    equipped:     ()            => api.get('/game/inventory/equipped/'),
    equipItem:    (id, action)  => api.post(`/game/inventory/${id}/equip/`, { action }),

    // ── Social ────────────────────────────────────────────────
    notifications:    ()     => api.get('/social/notifications/'),
    markAllRead:      ()     => api.post('/social/notifications/read-all/', {}),
    markRead:         (id)   => api.patch(`/social/notifications/${id}/read/`, {}),
    streak:           ()     => api.get('/social/streak/'),
    logActivity:      (type) => api.post('/social/activity/log/', { activity_type: type }),
    peerReviewQueue:       ()     => api.get('/social/peer-review/queue/'),
    submitPeerReview:      (data) => api.post('/social/peer-review/create/', data),
    myReviews:             (dir)  => api.get(`/social/peer-review/?direction=${dir || 'given'}`),
    peerReviewLeaderboard: ()     => api.get('/social/peer-review/leaderboard/'),

    // ── Admin monitoring ──────────────────────────────────────
    adminServerStatus: () => api.get('/auth/admin/server-status/'),
    adminSystemLogs:   (params) => api.get('/auth/admin/system-logs/' + (params ? '?' + new URLSearchParams(params) : '')),

    // ── Messages ──────────────────────────────────────────────
    msgInbox:      (params)  => api.get('/social/messages/inbox/' + (params ? '?' + new URLSearchParams(params) : '')),
    msgSent:       ()        => api.get('/social/messages/sent/'),
    msgDetail:     (id)      => api.get(`/social/messages/${id}/`),
    msgSend:       (data)    => api.post('/social/messages/', data),
    msgReply:      (id, data)=> api.post(`/social/messages/${id}/reply/`, data),
    msgRead:       (id)      => api.patch(`/social/messages/${id}/read/`, {}),
    msgUnread:     ()        => api.get('/social/messages/unread/'),
    msgRecipients: ()        => api.get('/social/messages/recipients/'),
  };
})();
