async function loadUsers() {
    showCreateButton(true, 'user');
    const res = await fetchWithAuth(`${API_BASE}/users`);
    if (!res) return;
    const users = await res.json();

    const rows = users.map(user => ({
        cells: [
            user.user_id,
            user.email,
            user.full_name || '',
            user.phone || '',
            user.role
        ],
        actions: `
            <button class="btn btn-outline-danger btn-sm btn-delete-user" data-id="${user.email}">
                <i class="fas fa-trash me-1"></i> Удалить
            </button>
        `
    }));

    renderTable('Пользователи', ['ID', 'Email', 'ФИО', 'Телефон', 'Роль'], rows);

    // Навешиваем обработчики после отрисовки таблицы
    const deleteButtons = document.querySelectorAll('.btn-delete-user');
    deleteButtons.forEach(btn => {
    btn.onclick = async (event) => {
        event.stopPropagation(); // Остановить всплытие, чтобы не срабатывал клик по строке
        const id = btn.dataset.id;
        if (!confirm('Удалить пользователя ' + id + '?')) return;

        const res = await fetchWithAuth(`${API_BASE}/users/detail/${id}`, {
            method: 'DELETE',
        });

        if (res && res.ok) {
            showNotification('Пользователь удалён');
            await loadUsers();
        }
    };
});

    // Навешиваем клики по строкам
    const tableRows = document.querySelectorAll('#excursionsTable tbody tr');
    tableRows.forEach(row => {
        row.onclick = () => {
            const cells = row.querySelectorAll('td');
            const username = cells[1].textContent;
            openEditUserModal(username);
        };
    });
}


document.getElementById('createUserForm').onsubmit = async (e) => {
    e.preventDefault();

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const full_name = document.getElementById('full_name').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const role_name = document.getElementById('role_name').value;

    if (!email || !password) {
        showNotification('Пожалуйста, заполните обязательные поля.');
        return;
    }

    const payload = {email, password, full_name, phone, role_name};

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

async function openEditUserModal(email) {
    const res = await fetchWithAuth(`${API_BASE}/users/detail/${email}`);
    if (!res || !res.ok) {
        showNotification('Не удалось загрузить пользователя');
        return;
    }

    const user = await res.json();

    document.getElementById('edit_email').value = user.email;
    document.getElementById('edit_full_name').value = user.full_name || '';
    document.getElementById('edit_phone').value = user.phone || '';
    document.getElementById('edit_password').value = '';
    document.getElementById('edit_role_name').value = user.role;

    new bootstrap.Modal(document.getElementById('editUserModal')).show();
}


document.getElementById('editUserForm').onsubmit = async (e) => {
    e.preventDefault();


    const email = document.getElementById('edit_email').value.trim();
    const password = document.getElementById('edit_password').value;
    const full_name = document.getElementById('edit_full_name').value.trim();
    const phone = document.getElementById('edit_phone').value.trim();
    const role_name = document.getElementById('edit_role_name').value;

    if (!email || !role_name) {
        showNotification('Пожалуйста, заполните обязательные поля.');
        return;
    }

    const payload = { email, full_name, phone, role_name };
    if (password) {
        if (password.length < 6) {
            showNotification('Пароль должен быть не менее 6 символов', 'warning');
            return;
        }
        payload.password = password;
    }

    const res = await fetchWithAuth(`${API_BASE}/users/detail/${email}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });

    if (res && res.ok) {
        showNotification('Пользователь обновлён');
        bootstrap.Modal.getInstance(document.getElementById('editUserModal')).hide();
        loadUsers();
    } else {
        const err = await res.json();
        showNotification(err.message || 'Ошибка при обновлении пользователя');
    }
};
