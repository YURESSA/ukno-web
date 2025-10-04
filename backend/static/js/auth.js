const API_BASE = '/api/admin';
const API_REF_BASE = '/api/references';
const TOKEN = localStorage.getItem('jwt_token');

if (!TOKEN) {
    showNotification('Не найден токен авторизации. Пожалуйста, выполните вход.');
    window.location.href = '/login-admin';
}

function showNotification(message, type = 'info', delay = 2500) {
    const id = 'toast_' + Date.now();
    const colors = {
        info: 'text-bg-info',
        success: 'text-bg-success',
        danger: 'text-bg-danger',
        warning: 'text-bg-warning',
    };

    const toastHTML = `
    <div id="${id}" class="toast align-items-center ${colors[type] || 'text-bg-info'} border-0 mb-2" role="showNotification" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Закрыть"></button>
      </div>
    </div>
  `;

    const area = document.getElementById('notificationArea');
    area.insertAdjacentHTML('beforeend', toastHTML);

    const toastEl = document.getElementById(id);
    const toast = new bootstrap.Toast(toastEl, { delay });
    toast.show();

    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
}

async function fetchWithAuth(url, options = {}) {
    options.headers = options.headers || {};
    options.headers['Authorization'] = 'Bearer ' + TOKEN;
    options.headers['Accept'] = 'application/json';

    try {
        const res = await fetch(url, options);
        console.log(res.status);
        if (res.status === 401 || res.status === 403) {
            showNotification('Сессия истекла. Пожалуйста, войдите заново.');
            window.location.href = '/login-admin';
            return null;
        }
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            showNotification('Ошибка: ' + (err.message || res.statusText));
            return null;
        }
        return res;
    } catch (e) {
        showNotification('Ошибка сети или сервера');
        return null;
    }
}
