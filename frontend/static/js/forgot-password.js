let currentEmail = '';
let currentCode  = '';

function showAlert(msg, type = 'error') {
  const box = document.getElementById('alertBox');
  box.className = `alert ${type}`;
  box.textContent = msg;
  box.style.display = 'block';
  setTimeout(() => { box.style.display = 'none'; }, 5000);
}

function setStep(n) {
  document.querySelectorAll('.step').forEach((s, i) => {
    s.classList.toggle('active', i + 1 === n);
  });
  document.querySelectorAll('.step-dot').forEach((d, i) => {
    if (i + 1 < n)       { d.className = 'step-dot done'; d.textContent = '✓'; }
    else if (i + 1 === n) { d.className = 'step-dot active'; d.textContent = i + 1; }
    else                   { d.className = 'step-dot pending'; d.textContent = i + 1; }
  });
}

async function sendCode() {
  const email = document.getElementById('emailInput').value.trim();
  if (!email) { showAlert('Email kiriting.'); return; }

  const btn = document.getElementById('sendBtn');
  btn.disabled = true;
  btn.textContent = 'Yuborilmoqda...';

  try {
    await api.forgotPassword(email);
    currentEmail = email;
    showAlert('Kod emailingizga yuborildi!', 'success');
    setTimeout(() => setStep(2), 800);
  } catch (e) {
    showAlert(e.message || 'Xatolik yuz berdi.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Kod yuborish';
  }
}

function verifyCode() {
  const code = document.getElementById('codeInput').value.trim();
  if (code.length !== 6) { showAlert('6 xonali kodni to\'liq kiriting.'); return; }
  currentCode = code;
  setStep(3);
}

function goBack() {
  setStep(1);
  document.getElementById('alertBox').style.display = 'none';
}

async function resendCode() {
  if (!currentEmail) { showAlert('Avval emailingizni kiriting.'); return; }
  try {
    await api.forgotPassword(currentEmail);
    showAlert('Kod qayta yuborildi!', 'success');
  } catch (e) {
    showAlert(e.message || 'Xatolik.');
  }
}

async function doReset() {
  const newPass     = document.getElementById('newPassInput').value;
  const confirmPass = document.getElementById('confirmPassInput').value;

  if (newPass.length < 8) { showAlert('Parol kamida 8 belgi bo\'lishi kerak.'); return; }
  if (newPass !== confirmPass) { showAlert('Parollar mos kelmadi.'); return; }

  const btn = document.getElementById('resetBtn');
  btn.disabled = true;
  btn.textContent = 'Yangilanmoqda...';

  try {
    await api.resetPassword({
      email: currentEmail,
      code:  currentCode,
      new_password: newPass,
    });
    showAlert('✅ Parol muvaffaqiyatli yangilandi!', 'success');
    setTimeout(() => { window.location.href = '/login.html'; }, 1500);
  } catch (e) {
    showAlert(e.message || 'Xatolik. Kodni tekshiring.');
    btn.disabled = false;
    btn.textContent = 'Parolni yangilash';
  }
}

document.addEventListener('keydown', e => {
  if (e.key !== 'Enter') return;
  const step = document.querySelector('.step.active');
  if (step?.id === 'step1') sendCode();
  if (step?.id === 'step2') verifyCode();
  if (step?.id === 'step3') doReset();
});
