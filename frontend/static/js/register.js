Auth.redirectIfAuthed();

const otps = document.querySelectorAll('.otp');
let regEmail = '';

function goPage(n) {
  document.querySelectorAll('.page').forEach((p, i) => p.classList.toggle('active', i === n - 1));
  ['s1','s2','s3'].forEach((id, i) => {
    const el = document.getElementById(id);
    el.classList.remove('active','done');
    if (i === n - 1) el.classList.add('active');
    else if (i < n - 1) el.classList.add('done');
  });
}

function goPage2() {
  const fn = document.getElementById('firstName').value.trim();
  const ln = document.getElementById('lastName').value.trim();
  let ok = true;
  document.getElementById('fnErr').style.display = fn ? 'none' : 'block'; if (!fn) ok = false;
  document.getElementById('lnErr').style.display = ln ? 'none' : 'block'; if (!ln) ok = false;
  if (ok) goPage(2);
}

function checkPass(v) {
  const bar = document.getElementById('pBar');
  const hint = document.getElementById('pHint');
  const s = [v.length >= 8, /[A-Z]/.test(v), /[0-9]/.test(v), /[^A-Za-z0-9]/.test(v)].filter(Boolean).length;
  bar.style.width = (s * 25) + '%';
  bar.style.background = ['','#ff6584','#ffa500','#4299e1','#43e97b'][s];
  hint.textContent = 'Parol kuchi: ' + (['','Zaif',"O'rtacha",'Yaxshi','Kuchli'][s] || '—');
}

async function goPage3() {
  const email    = document.getElementById('email').value.trim();
  const username = document.getElementById('username').value.trim();
  const p1       = document.getElementById('pass1').value;
  const p2       = document.getElementById('pass2').value;
  const terms    = document.getElementById('terms').checked;
  let ok = true;

  document.getElementById('emailErr').style.display = /\S+@\S+\.\S+/.test(email) ? 'none' : 'block';
  if (!/\S+@\S+\.\S+/.test(email)) ok = false;
  document.getElementById('unErr').style.display = username.length >= 3 ? 'none' : 'block';
  if (username.length < 3) ok = false;
  document.getElementById('p2Err').style.display = p1 === p2 ? 'none' : 'block';
  if (p1 !== p2) ok = false;
  if (!terms) { alert('Foydalanish shartlariga rozilik bildiring!'); ok = false; }
  if (!ok) return;

  const btn = document.querySelector('#pg2 .btn');
  btn.textContent = 'Yuklanmoqda...'; btn.disabled = true;

  try {
    await api.register({
      username, email,
      first_name: document.getElementById('firstName').value.trim(),
      last_name:  document.getElementById('lastName').value.trim(),
      password: p1, password2: p2,
      role: 'student',
    });
    regEmail = email;
    document.getElementById('sentTo').textContent = email;
    goPage(3);
  } catch (err) {
    alert('Xatolik: ' + err.message);
  } finally {
    btn.textContent = 'Tasdiqlash →'; btn.disabled = false;
  }
}

function otpNext(el, i) {
  el.value = el.value.replace(/\D/, '');
  if (el.value && i < 5) otps[i + 1].focus();
  if (i === 5) {
    const code = [...otps].map(o => o.value).join('');
    if (code.length === 6) verifyOTP();
  }
}

async function verifyOTP() {
  const code = [...otps].map(o => o.value).join('');
  if (code.length < 6) return;
  const btn = document.querySelector('#pg3 .btn');
  btn.textContent = 'Tekshirilmoqda...'; btn.disabled = true;
  try {
    await api.verifyOtp({ email: regEmail, code });
    window.location.href = '/login.html?verified=1';
  } catch (err) {
    otps.forEach(o => { o.style.borderColor = '#ff6584'; o.value = ''; });
    otps[0].focus();
    setTimeout(() => otps.forEach(o => o.style.borderColor = ''), 1500);
    alert(err.message || 'Kod noto\'g\'ri. Qayta urinib ko\'ring.');
  } finally {
    btn.textContent = 'Tasdiqlash ✓'; btn.disabled = false;
  }
}

async function resendCode() {
  if (!regEmail) return;
  try {
    await api.resendOtp(regEmail);
    alert('Kod qayta yuborildi!');
  } catch (err) { alert(err.message); }
}
