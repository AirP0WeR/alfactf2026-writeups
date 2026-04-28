(function () {
  const form = document.getElementById('auth-form');
  const usernameEl = document.getElementById('auth-username');
  const passwordEl = document.getElementById('auth-password');
  const submitBtn = document.getElementById('auth-submit');
  const errorEl = document.getElementById('auth-error');
  const tabLogin = document.getElementById('auth-tab-login');
  const tabRegister = document.getElementById('auth-tab-register');

  let mode = 'login';

  function setMode(next) {
    mode = next;
    tabLogin.classList.toggle('active', mode === 'login');
    tabRegister.classList.toggle('active', mode === 'register');
    submitBtn.textContent = mode === 'login' ? 'Войти' : 'Зарегистрироваться';
    passwordEl.setAttribute('autocomplete', mode === 'login' ? 'current-password' : 'new-password');
    errorEl.textContent = '';
  }

  tabLogin.addEventListener('click', () => setMode('login'));
  tabRegister.addEventListener('click', () => setMode('register'));

  function showError(key) {
    const messages = {
      invalid_username: 'Имя: минимум 9 символов, только буквы, цифры и _',
      invalid_password: 'Пароль должен быть не короче 9 символов',
      already_exists: 'Такой пользователь уже существует',
      invalid_credentials: 'Неверное имя пользователя или пароль',
      bad_request: 'Неверный запрос',
    };
    errorEl.textContent = messages[key] || 'Что-то пошло не так';
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorEl.textContent = '';
    const username = usernameEl.value.trim();
    const password = passwordEl.value;
    if (!username || !password) return;

    const endpoint = mode === 'login' ? '/login' : '/register';
    submitBtn.disabled = true;
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
        credentials: 'same-origin',
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data.ok) {
        showError(data.error);
        submitBtn.disabled = false;
        return;
      }
      
      window.location.href = '/';
    } catch (err) {
      errorEl.textContent = 'Ошибка подключения к серверу';
      submitBtn.disabled = false;
    }
  });

  fetch('/whoami', { credentials: 'same-origin' })
    .then((r) => r.json())
    .then((d) => {
      if (d && d.authenticated) {
        window.location.href = '/';
      }
    })
    .catch(() => {});
})();
