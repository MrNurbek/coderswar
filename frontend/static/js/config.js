/* ═══════════════════════════════════════════════
   Coders War — Global Config
   ═══════════════════════════════════════════════ */

// Production: nginx /api/ → Daphne
// Local dev:  VS Code Live Server (127.0.0.1:5500) → Django (127.0.0.1:8000)
const _isLocalDev = ['localhost', '127.0.0.1'].includes(window.location.hostname)
                    && window.location.port !== '';
const API_BASE = _isLocalDev ? 'http://127.0.0.1:8000/api' : '/api';

// Sahifa yo'llari — nisbiy yo'llar ishlatiladi (file:// va nginx ikkisida ham ishlaydi)
const ROUTES = {
  login:             'login.html',
  register:          'register.html',
  diagnostic:        'diagnostic.html',
  dashboard:         'dashboard.html',
  mainquest:         'mainquest.html',
  sidequest:         'sidequest.html',
  profile:           'profile.html',
  character:         'character.html',
  teacherDashboard:  'teacher-dashboard.html',
  adminDashboard:    'admin-dashboard.html',
};
