const API_BASE = '/api/admin';
const API_REF_BASE = '/api/references';
const TOKEN = localStorage.getItem('jwt_token');

if (!TOKEN) {
  showNotification('Не найден токен авторизации. Пожалуйста, выполните вход.');
  window.location.href = '/login';
}

function showNotification(message, type = 'info', delay = 3000) {
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

  // Удалить DOM-элемент после скрытия
  toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
}


async function fetchWithAuth(url, options = {}) {
  options.headers = options.headers || {};
  options.headers['Authorization'] = 'Bearer ' + TOKEN;
  options.headers['Accept'] = 'application/json';

  try {
    const res = await fetch(url, options);
    if (res.status === 401) {
      showNotification('Сессия истекла. Пожалуйста, войдите заново.');
      window.location.href = '/login';
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

function renderTable(title, headers, rows) {
  let html = `
    <div class="container mt-4">
      <h2 class="mb-3">${title}</h2>`;

  if (rows.length === 0) {
    html += `
      <div class="showNotification showNotification-info" role="showNotification">
        Данные отсутствуют.
      </div>`;
  } else {
    html += `
      <div class="table-responsive">
        <table class="table table-hover table-striped align-middle">
          <thead class="table-dark">
            <tr>`;

    for (const h of headers) {
      html += `<th scope="col">${h}</th>`;
    }
    html += `<th scope="col" style="width: 130px;">Действия</th>`;

    html += `</tr>
          </thead>
          <tbody>`;

    for (const row of rows) {
      html += '<tr>';
      for (const cell of row.cells) {
        html += `<td>${cell}</td>`;
      }
      html += `<td>${row.actions}</td>`;
      html += '</tr>';
    }

    html += `
          </tbody>
        </table>
      </div>`;
  }

  html += `</div>`;
  document.getElementById('contentArea').innerHTML = html;
}


async function loadUsers() {
  showCreateButton(true, 'user');
  const res = await fetchWithAuth(`${API_BASE}/users`);
  if (!res) return;
  const users = await res.json();

  const rows = users.map(user => ({
    cells: [
      user.username,
      user.email,
      user.full_name || '',
      user.phone || '',
      user.role
    ],
    actions: `
      <button class="btn btn-danger btn-sm btn-delete-user" data-id="${user.username}">
        <i class="fas fa-trash"></i> Удалить
      </button>`
  }));

  renderTable('Пользователи', ['Логин', 'Email', 'ФИО', 'Телефон', 'Роль'], rows);

  document.querySelectorAll('.btn-delete-user').forEach(btn => {
    btn.onclick = async () => {
      const id = btn.dataset.id;
      if (!confirm('Удалить пользователя ' + id + '?')) return;

      const res = await fetchWithAuth(`${API_BASE}/users/detail/${id}`, {
        method: 'DELETE',
      });
      if (res) {
        showNotification('Пользователь удалён');
        loadUsers();
      }
    };
  });
}

async function loadRoles() {
  showCreateButton(false);
  const res = await fetchWithAuth(`${API_BASE}/roles`);
  if (!res) return;
  const roles = await res.json();

  const rows = roles.map(role => ({
    cells: [role.role_id, role.role_name],
    actions: ''
  }));

  renderTable('Роли', ['ID', 'Название'], rows);
}

const urlMap = {
  'categories': `${API_REF_BASE}/categories`,
  'format-types': `${API_REF_BASE}/format-types`,
  'age-categories': `${API_REF_BASE}/age-categories`,
};

const titles = {
  'categories': 'Категории',
  'format-types': 'Типы форматов',
  'age-categories': 'Возрастные категории',
};

const idFields = {
  'categories': 'category_id',
  'format-types': 'format_type_id',
  'age-categories': 'age_category_id',
};

const nameFields = {
  'categories': 'category_name',
  'format-types': 'format_type_name',
  'age-categories': 'age_category_name',
};

let currentRef = null; // чтобы знать какой справочник открыт

async function loadReference(refName) {
  showCreateButton(true, 'ref');
  currentRef = refName;

  const url = urlMap[refName];
  if (!url) return showNotification('Неизвестный справочник ' + refName);

  const res = await fetchWithAuth(url);
  if (!res) return;
  const data = await res.json();

  const rows = data.map(item => ({
    cells: [item[idFields[refName]], item[nameFields[refName]]],
    actions: `
      <button class="btn btn-danger btn-sm btn-delete-ref" data-ref="${refName}" data-id="${item[idFields[refName]]}">
        <i class="fas fa-trash"></i> Удалить
      </button>`
  }));

  renderTable(titles[refName], ['ID', 'Название'], rows);

  document.querySelectorAll('.btn-delete-ref').forEach(btn => {
    btn.onclick = async () => {
      const id = btn.dataset.id;
      const ref = btn.dataset.ref;
      if (!confirm(`Удалить элемент #${id} из ${titles[ref]}?`)) return;

      const res = await fetchWithAuth(`${API_REF_BASE}/${ref}/${id}`, { method: 'DELETE' });
      if (res) {
        showNotification('Элемент удалён');
        loadReference(ref);
      }
    };
  });
}

// Показ кнопки создания в зависимости от активного раздела
function showCreateButton(show, type) {
  const btnUser = document.getElementById('btnCreateUser');
  const btnRef = document.getElementById('btnCreateRef');
  if (type === 'user') {
    btnUser.style.display = show ? 'inline-block' : 'none';
    btnRef.style.display = 'none';
  } else if (type === 'ref') {
    btnUser.style.display = 'none';
    btnRef.style.display = show ? 'inline-block' : 'none';
  } else {
    btnUser.style.display = 'none';
    btnRef.style.display = 'none';
  }
}

// Кнопки меню с сохранением текущего раздела
document.getElementById('btnUsers').onclick = e => {
  e.preventDefault();
  setActiveMenu('btnUsers');
  localStorage.setItem('admin_current_section', 'users');
  loadUsers();
};

document.getElementById('btnRoles').onclick = e => {
  e.preventDefault();
  setActiveMenu('btnRoles');
  localStorage.setItem('admin_current_section', 'roles');
  loadRoles();
};

document.getElementById('btnCategories').onclick = e => {
  e.preventDefault();
  setActiveMenu('btnCategories');
  localStorage.setItem('admin_current_section', 'categories');
  loadReference('categories');
};

document.getElementById('btnFormatTypes').onclick = e => {
  e.preventDefault();
  setActiveMenu('btnFormatTypes');
  localStorage.setItem('admin_current_section', 'format-types');
  loadReference('format-types');
};

document.getElementById('btnAgeCategories').onclick = e => {
  e.preventDefault();
  setActiveMenu('btnAgeCategories');
  localStorage.setItem('admin_current_section', 'age-categories');
  loadReference('age-categories');
};

function setActiveMenu(id) {
  document.querySelectorAll('#sidebar .nav-link').forEach(link => {
    link.classList.remove('active');
  });
  document.getElementById(id).classList.add('active');
}

// Создание пользователя
document.getElementById('createUserForm').onsubmit = async (e) => {
  e.preventDefault();

  const username = document.getElementById('username').value.trim();
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const full_name = document.getElementById('full_name').value.trim();
  const phone = document.getElementById('phone').value.trim();
  const role_name = document.getElementById('role_name').value;

  if (!username || !email || !password) {
    showNotification('Пожалуйста, заполните обязательные поля.');
    return;
  }

  const payload = { username, email, password, full_name, phone, role_name };

  const res = await fetchWithAuth(`${API_BASE}/users`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload),
  });

  if (res) {
    showNotification('Пользователь успешно создан');
    e.target.reset();
    const modal = bootstrap.Modal.getInstance(document.getElementById('createUserModal'));
    modal.hide();

    loadUsers();
  }
};

// Обработка создания записи в справочнике из модалки
document.getElementById('createRefForm').onsubmit = async (e) => {
  e.preventDefault();

  const name = document.getElementById('refNameInput').value.trim();
  if (!name) {
    showNotification('Пожалуйста, введите название');
    return;
  }

  if (!currentRef) {
    showNotification('Не выбран тип справочника');
    return;
  }

  const payload = { name };

  const res = await fetchWithAuth(`${API_REF_BASE}/${currentRef}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (res) {
    showNotification('Запись успешно создана');
    const modal = bootstrap.Modal.getInstance(document.getElementById('createRefModal'));
    modal.hide();
    loadReference(currentRef);
  }
};

// Кнопка "Создать запись" для справочников
document.getElementById('btnCreateRef').onclick = () => {
  if (!currentRef) {
    showNotification('Сначала выберите раздел справочника');
    return;
  }
  // Очистить поле ввода
  document.getElementById('refNameInput').value = '';
  // Показать модалку
  const modal = new bootstrap.Modal(document.getElementById('createRefModal'));
  modal.show();
};

// Загрузка последнего открытого раздела при загрузке страницы
window.onload = () => {
  const section = localStorage.getItem('admin_current_section');

  switch (section) {
    case 'users':
      setActiveMenu('btnUsers');
      loadUsers();
      break;
    case 'roles':
      setActiveMenu('btnRoles');
      loadRoles();
      break;
    case 'categories':
      setActiveMenu('btnCategories');
      loadReference('categories');
      break;
    case 'format-types':
      setActiveMenu('btnFormatTypes');
      loadReference('format-types');
      break;
    case 'age-categories':
      setActiveMenu('btnAgeCategories');
      loadReference('age-categories');
      break;
    default:
      setActiveMenu('btnUsers');
      loadUsers();
      break;
  }
};
