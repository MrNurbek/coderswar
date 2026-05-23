Auth.redirectIfAuthed();

function togglePass() {
  const i = document.getElementById('passInput');
  i.type = i.type === 'password' ? 'text' : 'password';
}

function showError(msg) {
  const el = document.getElementById('errMsg');
  el.textContent = msg;
  el.style.display = 'block';
}

async function handleLogin(e) {
  e.preventDefault();
  const btn = document.getElementById('loginBtn');
  const errEl = document.getElementById('errMsg');
  errEl.style.display = 'none';
  btn.textContent = 'Kirish...';
  btn.disabled = true;

  const username = document.getElementById('loginInput').value.trim();
  const password = document.getElementById('passInput').value;

  try {
    const user = await Auth.login(username, password);
    if (user.role === 'teacher' || user.role === 'admin' || user.role === 'superadmin') {
      window.location.href = '/teacher-dashboard.html';
    } else {
      window.location.href = user.student_profile ? '/dashboard.html' : '/diagnostic.html';
    }
  } catch (err) {
    showError(err.message || 'Login yoki parol noto\'g\'ri.');
    btn.textContent = 'Kirish →';
    btn.disabled = false;
  }
}

function demoLogin() {
  document.getElementById('loginInput').value = 'demo';
  document.getElementById('passInput').value = 'demo1234';
  document.getElementById('loginForm').requestSubmit();
}
