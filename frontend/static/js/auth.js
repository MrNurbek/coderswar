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

  // ── Rolga qarab yo'naltirish ─────────────────
  function roleRedirect(user) {
    const role = user?.role;
    if (role === 'admin' || role === 'superadmin') {
      window.location.href = ROUTES.adminDashboard;
    } else if (role === 'teacher') {
      window.location.href = ROUTES.teacherDashboard;
    } else {
      // Personaj tanlanmagan bo'lsa — onboarding (diagnostic → character)
      const hasCharacter = user?.student_profile?.character;
      window.location.href = hasCharacter ? ROUTES.dashboard : ROUTES.diagnostic;
    }
  }

  // ── Allaqachon login bo'lgan bo'lsa ──────────
  function redirectIfAuthed() {
    if (getAccess()) {
      roleRedirect(getUser());
      return true;
    }
    return false;
  }

  // ── Sidebar / topbar ga foydalanuvchi info ───
  function fillUserUI() {
    const u = getUser();
    if (!u) return;
    const name  = u.first_name ? `${u.first_name} ${u.last_name}`.trim() : u.username;
    const roleMap = { teacher: 'O\'qituvchi', admin: 'Admin', superadmin: 'Admin' };
    const role  = roleMap[u.role] || 'Talaba';
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

  function isLoggedIn() { return !!getAccess(); }

  return {
    getAccess, getRefresh, setTokens, clearAll,
    getUser, setUser, refreshToken,
    login, fetchMe, logout,
    requireAuth, redirectIfAuthed, roleRedirect, fillUserUI,
    isLoggedIn,
  };
})();

/* ── Sahifalar orasida so'zsiz o'tish (fade) ─────────────── */
(function () {
  // Sahifa yuklanganda opacity 0 dan boshlanadi
  document.documentElement.style.opacity = '0';

  function fadeIn() {
    requestAnimationFrame(() => {
      document.documentElement.style.transition = 'opacity .25s ease';
      document.documentElement.style.opacity    = '1';
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fadeIn);
  } else {
    fadeIn();
  }

  // <a href> bosilganda fade-out, keyin navigate
  document.addEventListener('click', function (e) {
    const a = e.target.closest('a[href]');
    if (!a) return;
    const href = a.getAttribute('href');
    if (
      !href ||
      href[0] === '#' ||                // anchor
      href.startsWith('http') ||        // tashqi havola
      href.startsWith('mailto:') ||     // email
      a.getAttribute('target') === '_blank'
    ) return;
    e.preventDefault();
    document.documentElement.style.transition = 'opacity .2s ease';
    document.documentElement.style.opacity    = '0';
    setTimeout(() => { location.href = href; }, 210);
  });
})();
