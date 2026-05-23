/* ═══════════════════════════════════════════════
   Coders War — Auth Manager (JWT)
   ═══════════════════════════════════════════════ */

const Auth = (() => {
  const KEYS = { access: 'cw_access', refresh: 'cw_refresh', user: 'cw_user' };

  // ── Token saqlash / olish ────────────────────
  function getAccess()  { return localStorage.getItem(KEYS.access); }
  function getRefresh() { return localStorage.getItem(KEYS.refresh); }

  function setTokens(access, refresh) {
    localStorage.setItem(KEYS.access, access);
    if (refresh) localStorage.setItem(KEYS.refresh, refresh);
  }

  function clearAll() {
    Object.values(KEYS).forEach(k => localStorage.removeItem(k));
  }

  // ── Foydalanuvchi ma'lumotlari ───────────────
  function getUser() {
    try { return JSON.parse(localStorage.getItem(KEYS.user)); }
    catch { return null; }
  }

  function setUser(u) {
    localStorage.setItem(KEYS.user, JSON.stringify(u));
  }

  // ── Token yangilash ──────────────────────────
  async function refreshToken() {
    const refresh = getRefresh();
    if (!refresh) return false;
    try {
      const res = await fetch(`${API_BASE}/auth/token/refresh/`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ refresh }),
      });
      if (!res.ok) { clearAll(); return false; }
      const data = await res.json();
      setTokens(data.access, data.refresh || null);
      return true;
    } catch { return false; }
  }

  // ── Login ────────────────────────────────────
  async function login(username, password) {
    const res = await fetch(`${API_BASE}/auth/token/`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Login yoki parol noto\'g\'ri.');
    }
    const data = await res.json();
    setTokens(data.access, data.refresh);

    // Profil yuklab olish
    const me = await fetchMe(data.access);
    setUser(me);
    return me;
  }

  // ── Profil ───────────────────────────────────
  async function fetchMe(token) {
    const t = token || getAccess();
    const res = await fetch(`${API_BASE}/auth/me/`, {
      headers: { Authorization: `Bearer ${t}` },
    });
    if (!res.ok) throw new Error('Profil yuklanmadi.');
    return res.json();
  }

  // ── Chiqish ──────────────────────────────────
  function logout() {
    clearAll();
    window.location.href = ROUTES.login;
  }

  // ── Auth tekshiruv (sahifa yuklanganda) ──────
  function requireAuth() {
    if (!getAccess()) {
      window.location.href = ROUTES.login;
      return false;
    }
    return true;
  }

  // ── Allaqachon login bo'lgan bo'lsa ──────────
  function redirectIfAuthed() {
    if (getAccess()) {
      const user = getUser();
      if (user?.role === 'teacher') window.location.href = '/teacher-dashboard.html';
      else window.location.href = ROUTES.dashboard;
      return true;
    }
    return false;
  }

  // ── Sidebar / topbar ga foydalanuvchi info ───
  function fillUserUI() {
    const u = getUser();
    if (!u) return;
    const name  = u.first_name ? `${u.first_name} ${u.last_name}`.trim() : u.username;
    const role  = u.role === 'teacher' ? 'O\'qituvchi' : 'Talaba';
    const init  = (name[0] || 'U').toUpperCase();

    document.querySelectorAll('[data-user-name]').forEach(el => el.textContent = name);
    document.querySelectorAll('[data-user-role]').forEach(el => el.textContent = role);
    document.querySelectorAll('[data-user-init]').forEach(el => el.textContent = init);
    document.querySelectorAll('[data-user-avatar]').forEach(el => {
      if (u.avatar) { el.style.backgroundImage = `url(${u.avatar})`; el.textContent = ''; }
      else el.textContent = init;
    });
    document.querySelectorAll('.logout-btn').forEach(el => {
      el.addEventListener('click', logout);
    });
  }

  return {
    getAccess, getRefresh, setTokens, clearAll,
    getUser, setUser, refreshToken,
    login, fetchMe, logout,
    requireAuth, redirectIfAuthed, fillUserUI,
  };
})();
