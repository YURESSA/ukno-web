const API_BASE = '/api/admin';
const API_REF_BASE = '/api/references';
const TOKEN = localStorage.getItem('jwt_token');

if (!TOKEN) {
    showNotification('Не найден токен авторизации. Пожалуйста, выполните вход.');
    window.location.href = '/login';
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
    const toast = new bootstrap.Toast(toastEl, {delay});
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
        <table id="excursionsTable" class="table table-hover table-striped align-middle">
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
            // Добавляем data-id к tr
            html += `<tr data-id="${row.id || ''}" style="cursor: pointer;">`;
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

            const res = await fetchWithAuth(`${API_REF_BASE}/${ref}/${id}`, {method: 'DELETE'});
            if (res) {
                showNotification('Элемент удалён');
                loadReference(ref);
            }
        };
    });
}

async function loadExcursions() {
    showCreateButton(false);
    const res = await fetchWithAuth(`${API_BASE}/excursions`);
    if (!res) return;
    const data = await res.json();

    // Формируем строки с id экскурсии
    const rows = data.excursions.map(item => ({
        id: item.excursion_id,  // добавляем id
        cells: [
            item.title,
            (item.description ? item.description.slice(0, 100) + '...' : ''),
            item.category?.category_name || '',
            item.format_type?.format_type_name || '',
            item.age_category?.age_category_name || '',
        ],
        actions: `
          <button class="btn btn-danger btn-sm btn-delete-excursion" data-id="${item.excursion_id}">
            <i class="fas fa-trash"></i> Удалить
          </button>
        `
    }));

    renderTable('Экскурсии', ['Название', 'Описание', 'Категория', 'Формат', 'Возраст'], rows);

    // Навешиваем обработчик на строки таблицы для просмотра экскурсии
    document.querySelectorAll('#excursionsTable tbody tr').forEach(row => {
        row.onclick = async (e) => {
            // Если клик был на кнопке внутри строки — игнорируем, чтобы не открывать модалку
            if (e.target.closest('button')) return;

            const id = row.getAttribute('data-id');
            if (!id) return;
            const res = await fetchWithAuth(`${API_BASE}/excursions/${id}`);
            if (!res) {
                showNotification('Ошибка загрузки экскурсии', 'danger');
                return;
            }
            const data = await res.json();
            showExcursionModal(data.excursion);
        };
    });

    // Обработчик удаления экскурсии
    document.querySelectorAll('.btn-delete-excursion').forEach(btn => {
        btn.onclick = async (e) => {
            e.stopPropagation();  // чтобы не срабатывал клик по строке
            const id = btn.dataset.id;
            if (!confirm(`Удалить экскурсию #${id}?`)) return;

            const res = await fetchWithAuth(`${API_BASE}/excursions/${id}`, {method: 'DELETE'});
            if (res) {
                showNotification('Экскурсия удалена', 'success');
                loadExcursions(); // перезагрузить список
            }
        };
    });
}


let currentExcursionId = null;
let originalExcursionData = {};

function getChangedFields() {
    const updated = collectExcursionFormData();
    const changed = {};

    const fieldsToCheck = [
        'title', 'description', 'duration', 'place', 'conducted_by',
        'working_hours', 'contact_email', 'iframe_url',
        'telegram', 'vk', 'distance_to_center', 'time_to_nearest_stop',
        'is_active'
    ];

    for (const field of fieldsToCheck) {
        const original = originalExcursionData[field];

        if (['duration', 'distance_to_center', 'time_to_nearest_stop'].includes(field)) {
            const updatedValue = updated[field] !== '' ? Number(updated[field]) : null;
            const originalValue = original !== null && original !== undefined ? Number(original) : null;

            if (updatedValue !== originalValue) {
                changed[field] = updatedValue;
            }
        } else if (field === 'is_active') {
            const updatedValue = Boolean(updated[field]);
            const originalValue = Boolean(original);
            if (updatedValue !== originalValue) {
                changed[field] = updatedValue;
            }
        } else {
            const updatedValue = updated[field] || '';
            const originalValue = original || '';
            if (updatedValue !== originalValue || field === 'title') {
                // Гарантированно включаем title всегда
                changed[field] = updated[field];
            }
        }
    }

    return changed;
}


function showExcursionModal(excursion) {
    currentExcursionId = excursion.excursion_id || excursion.id || null;
    originalExcursionData = {...excursion};

    document.getElementById('modalTitle').value = excursion.title || '';
    document.getElementById('modalDescription').value = excursion.description || '';
    document.getElementById('modalCategory').value = excursion.category?.category_name || '';
    document.getElementById('modalFormat').value = excursion.format_type?.format_type_name || '';
    document.getElementById('modalAgeCategory').value = excursion.age_category?.age_category_name || '';
    document.getElementById('modalDuration').value = excursion.duration || '';
    document.getElementById('modalPlace').value = excursion.place || '';
    document.getElementById('modalConductedBy').value = excursion.conducted_by || '';
    document.getElementById('modalWorkingHours').value = excursion.working_hours || '';
    document.getElementById('modalContactEmail').value = excursion.contact_email || '';
    document.getElementById('modalTelegram').value = excursion.telegram || '';
    document.getElementById('modalVk').value = excursion.vk || '';
    document.getElementById('modalIsActive').value = excursion.is_active ? 'true' : 'false';
    document.getElementById('modalDistance').value = excursion.distance_to_center ?? '';
    document.getElementById('modalTimeToStop').value = excursion.time_to_nearest_stop ?? '';
    document.getElementById('modalIframe').value = excursion.iframe_url ?? '';


    // Фотографии, сессии, теги оставим как есть (только для просмотра)
    excursionPhotosRender(excursion.photos);

    renderSessions(excursion.sessions);


    const tagsDiv = document.getElementById('modalTags');
    tagsDiv.innerHTML = '';
    if (excursion.tags?.length) {
        excursion.tags.forEach(tag => {
            const span = document.createElement('span');
            span.textContent = tag.name;
            span.style.marginRight = '8px';
            span.style.padding = '4px 8px';
            span.style.backgroundColor = '#e0e0e0';
            span.style.borderRadius = '4px';
            tagsDiv.appendChild(span);
        });
    } else {
        tagsDiv.textContent = 'Теги отсутствуют.';
    }

    // Показать модалку
    const modal = document.getElementById('excursionModal');
    modal.style.display = 'flex';
}


// Сбор данных из формы
function collectExcursionFormData() {
    return {
        title: document.getElementById('modalTitle').value,
        description: document.getElementById('modalDescription').value,
        category_name: document.getElementById('modalCategory').value,
        format_type_name: document.getElementById('modalFormat').value,
        age_category_name: document.getElementById('modalAgeCategory').value,
        duration: document.getElementById('modalDuration').value,
        place: document.getElementById('modalPlace').value,
        conducted_by: document.getElementById('modalConductedBy').value,
        working_hours: document.getElementById('modalWorkingHours').value,
        contact_email: document.getElementById('modalContactEmail').value,
        telegram: document.getElementById('modalTelegram').value,
        vk: document.getElementById('modalVk').value,
        is_active: document.getElementById('modalIsActive').value === 'true',
        distance_to_center: parseFloat(document.getElementById('modalDistance').value),
        time_to_nearest_stop: parseFloat(document.getElementById('modalTimeToStop').value),
    };
}

function openSessionModalForEdit(session) {
    document.getElementById('editingSessionId').value = session.session_id;
    document.getElementById('sessionDatetimeModal').value = session.start_datetime.slice(0, 16);
    document.getElementById('sessionCostModal').value = session.cost;
    document.getElementById('sessionMaxParticipantsModal').value = session.max_participants;

    document.getElementById('deleteSessionBtn').style.display = 'inline-block';
    sessionModal.show();
}

async function deleteSession(sessionId) {
    if (!confirm('Удалить сессию?')) return;

    try {
        const res = await fetchWithAuth(`/api/admin/excursions/${currentExcursionId}/sessions/${sessionId}`, {
            method: 'DELETE'
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.message || 'Ошибка удаления');
        }

        originalExcursionData.sessions = originalExcursionData.sessions.filter(s => s.session_id !== sessionId);
        renderSessions(originalExcursionData.sessions);

        showNotification('Сессия удалена', 'success');
    } catch (err) {
        showNotification('Ошибка: ' + err.message, 'danger');
    }
}


// Сохранение изменений
document.getElementById('modalSave').onclick = async () => {
    if (!currentExcursionId) {
        showNotification('ID экскурсии не найден', 'danger');
        return;
    }

    const changes = getChangedFields();
    if (Object.keys(changes).length === 0) {
        showNotification('Нет изменений для сохранения', 'info');
        return;
    }

    try {
        const res = await fetchWithAuth(`${API_BASE}/excursions/${currentExcursionId}`, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(changes),
        });

        if (!res.ok) {
            showNotification('Ошибка при обновлении экскурсии', 'danger');
            return;
        }

        showNotification('Экскурсия обновлена', 'success');
        loadExcursions();
        document.getElementById('excursionModal').style.display = 'none';
    } catch (e) {
        showNotification('Ошибка сети', 'danger');
    }
};


const modal = document.getElementById('excursionModal');

function closeModal() {
    modal.style.display = 'none';
}

document.getElementById('modalClose').onclick = closeModal;
document.getElementById('modalCloseFooter').onclick = closeModal;
window.onclick = (event) => {
    if (event.target === modal) {
        closeModal();
    }
};

const photoInput = document.getElementById('modalPhotoUpload');
const btnAddPhoto = document.getElementById('btnAddPhoto');
const photosDiv = document.getElementById('modalPhotos');

// Загрузка фото на сервер
btnAddPhoto.onclick = async () => {
    if (!currentExcursionId) {
        showNotification('Не выбрана экскурсия', 'danger');
        return;
    }

    const file = photoInput.files[0];
    if (!file) {
        showNotification('Выберите фото для загрузки', 'warning');
        return;
    }

    const formData = new FormData();
    formData.append('photo', file);

    try {
        const res = await fetchWithAuth(`${API_BASE}/excursions/${currentExcursionId}/photos`, {
            method: 'POST',
            body: formData,
        });

        if (!res.ok) {
            const errorData = await res.json();
            showNotification(errorData.message || 'Ошибка загрузки фото', 'danger');
            return;
        }

        const data = await res.json();
        showNotification('Фото добавлено', 'success');
        photoInput.value = ''; // очистить выбор файла
        excursionPhotosRender(data.photos);
    } catch (e) {
        showNotification('Ошибка сети при загрузке фото', 'danger');
    }
};

const renderSessions = (sessions) => {
    const sessionsDiv = document.getElementById('modalSessions');
    sessionsDiv.innerHTML = '';

    if (!sessions?.length) {
        sessionsDiv.textContent = 'Сессии отсутствуют.';
        return;
    }

    sessions.forEach(s => {
        const p = document.createElement('p');
        const date = new Date(s.start_datetime);
        p.textContent = `${date.toLocaleString()} — Стоимость: ${s.cost} руб, Участников: ${s.booked}/${s.max_participants}`;

        const editBtn = document.createElement('button');
        editBtn.textContent = '✎';
        editBtn.className = 'btn btn-sm btn-outline-primary ms-2';
        editBtn.onclick = () => openSessionModalForEdit(s);

        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = '🗑';
        deleteBtn.className = 'btn btn-sm btn-outline-danger ms-1';
        deleteBtn.onclick = () => deleteSession(s.session_id);

        p.appendChild(editBtn);
        p.appendChild(deleteBtn);
        sessionsDiv.appendChild(p);
    });
};


// Отрисовка списка фото с кнопками удаления
function excursionPhotosRender(photos) {
    photosDiv.innerHTML = '';
    if (!photos || photos.length === 0) {
        photosDiv.textContent = 'Фотографии отсутствуют.';
        return;
    }

    photos.forEach(photo => {
        const div = document.createElement('div');
        div.style.position = 'relative';
        div.style.display = 'inline-block';
        div.style.margin = '5px';

        const img = document.createElement('img');
        img.src = photo.photo_url.startsWith('/') ? photo.photo_url : '/' + photo.photo_url;
        img.style.width = '150px';
        img.style.height = 'auto';
        img.style.borderRadius = '5px';
        div.appendChild(img);

        const btnDelete = document.createElement('button');
        btnDelete.textContent = '×';
        btnDelete.title = 'Удалить фото';
        btnDelete.style.position = 'absolute';
        btnDelete.style.top = '5px';
        btnDelete.style.right = '5px';
        btnDelete.style.backgroundColor = 'rgba(255,0,0,0.7)';
        btnDelete.style.border = 'none';
        btnDelete.style.color = 'white';
        btnDelete.style.fontWeight = 'bold';
        btnDelete.style.borderRadius = '50%';
        btnDelete.style.cursor = 'pointer';

        btnDelete.onclick = async () => {
            if (!confirm('Удалить фото?')) return;

            try {
                const res = await fetchWithAuth(`${API_BASE}/excursions/${currentExcursionId}/photos/${photo.photo_id}`, {
                    method: 'DELETE',
                });

                if (!res.ok) {
                    showNotification('Ошибка удаления фото', 'danger');
                    return;
                }

                showNotification('Фото удалено', 'success');

                // Обновляем список фото после удаления
                const updatedPhotosRes = await fetchWithAuth(`${API_BASE}/excursions/${currentExcursionId}/photos`);
                if (updatedPhotosRes.ok) {
                    const updatedData = await updatedPhotosRes.json();
                    excursionPhotosRender(updatedData.photos);
                }
            } catch {
                showNotification('Ошибка сети при удалении фото', 'danger');
            }
        };

        div.appendChild(btnDelete);
        photosDiv.appendChild(div);
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


document.addEventListener('DOMContentLoaded', () => {
    window.sessionModal = new bootstrap.Modal(document.getElementById('sessionModal')); // глобально
    // остальные элементы
    const btnAddSession = document.getElementById('btnAddSession');
    const editingSessionId = document.getElementById('editingSessionId');
    const sessionDatetimeModal = document.getElementById('sessionDatetimeModal');
    const sessionCostModal = document.getElementById('sessionCostModal');
    const sessionMaxParticipantsModal = document.getElementById('sessionMaxParticipantsModal');
    const deleteSessionBtn = document.getElementById('deleteSessionBtn');

    btnAddSession.onclick = () => {
        editingSessionId.value = '';
        sessionDatetimeModal.value = '';
        sessionCostModal.value = '';
        sessionMaxParticipantsModal.value = '';

        deleteSessionBtn.style.display = 'none';
        window.sessionModal.show();
    };
});


document.getElementById('saveSessionModalBtn').addEventListener('click', async () => {
    const sessionId = document.getElementById('editingSessionId').value;
    const datetime = document.getElementById('sessionDatetimeModal').value;
    const cost = document.getElementById('sessionCostModal').value;
    const maxParticipants = document.getElementById('sessionMaxParticipantsModal').value;

    if (!datetime || !cost || !maxParticipants) {
        showNotification('Заполните все поля', 'warning');
        return;
    }

    const payload = {
        start_datetime: new Date(datetime).toISOString(),
        cost: Number(cost),
        max_participants: Number(maxParticipants),
    };

    const method = sessionId ? 'PATCH' : 'POST';
    const url = sessionId
        ? `/api/admin/excursions/${currentExcursionId}/sessions/${sessionId}`
        : `/api/admin/excursions/${currentExcursionId}/sessions`;

    try {
        const res = await fetchWithAuth(url, {
            method,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.message || 'Ошибка сохранения');
        }

        const updatedExcursion = await fetchWithAuth(`/api/admin/excursions/${currentExcursionId}`);
        if (updatedExcursion.ok) {
            const data = await updatedExcursion.json();
            originalExcursionData.sessions = data.excursion.sessions;
            renderSessions(originalExcursionData.sessions);
        }

        showNotification('Сессия сохранена', 'success');
        window.sessionModal.hide();
    } catch (err) {
        showNotification('Ошибка: ' + err.message, 'danger');
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const btnAddSession = document.getElementById('btnAddSession');
    const editingSessionId = document.getElementById('editingSessionId');
    const sessionDatetimeModal = document.getElementById('sessionDatetimeModal');
    const sessionCostModal = document.getElementById('sessionCostModal');
    const sessionMaxParticipantsModal = document.getElementById('sessionMaxParticipantsModal');
    const deleteSessionBtn = document.getElementById('deleteSessionBtn');

    btnAddSession.onclick = () => {
        editingSessionId.value = '';
        sessionDatetimeModal.value = '';
        sessionCostModal.value = '';
        sessionMaxParticipantsModal.value = '';

        deleteSessionBtn.style.display = 'none';
        sessionModal.show();
    };
});


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

    const payload = {username, email, password, full_name, phone, role_name};

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

    const payload = {name};

    const res = await fetchWithAuth(`${API_REF_BASE}/${currentRef}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
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

document.getElementById('btnExcursions').onclick = e => {
    e.preventDefault();
    setActiveMenu('btnExcursions');
    localStorage.setItem('admin_current_section', 'excursions');
    loadExcursions();
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
        case 'excursions':
            setActiveMenu('btnExcursions');
            loadExcursions();
            break;
        default:
            setActiveMenu('btnUsers');
            loadUsers();
            break;
    }
};

