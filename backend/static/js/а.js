async function loadUsers() {
    showCreateButton(true, 'user');
    const res = await fetchWithAuth(`${API_BASE}/users`);
    if (!res) return;
    const users = await res.json();

    const rows = users.map(user => ({
        cells: [
            user.user_id,
            user.username,
            user.email,
            user.full_name || '',
            user.phone || '',
            user.role
        ],
        actions: `
      <button class="btn btn-outline-danger btn-sm btn-delete-user" data-id="${user.username}">
          <i class="fas fa-trash me-1"></i> Удалить
        </button>
`
    }));

    renderTable('Пользователи', ['ID', 'Логин', 'Email', 'ФИО', 'Телефон', 'Роль'], rows);

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

    document.querySelectorAll('#excursionsTable tbody tr').forEach(row => {
        row.addEventListener('click', () => {
            const cells = row.querySelectorAll('td');
            const username = cells[1].textContent;

            openEditUserModal(username);
        });
    });
}

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

async function openEditUserModal(username) {
    const res = await fetchWithAuth(`${API_BASE}/users/detail/${username}`);
    if (!res.ok) {
        showNotification('Не удалось загрузить данные пользователя');
        return;
    }

    const user = await res.json();

    document.getElementById('edit_user_id').value = user.user_id;
    document.getElementById('edit_username').value = user.username;
    document.getElementById('edit_email').value = user.email;
    document.getElementById('edit_full_name').value = user.full_name || '';
    document.getElementById('edit_phone').value = user.phone || '';
    document.getElementById('edit_password').value = '';
    document.getElementById('edit_role_id').value = user.role_id;

    new bootstrap.Modal(document.getElementById('editUserModal')).show();
}

document.getElementById('editUserForm').onsubmit = async (e) => {
    e.preventDefault();

    const username = document.getElementById('edit_username').value;
    const email = document.getElementById('edit_email').value.trim();
    const full_name = document.getElementById('edit_full_name').value.trim();
    const phone = document.getElementById('edit_phone').value.trim();
    const password = document.getElementById('edit_password').value;
    const role_id = parseInt(document.getElementById('edit_role_id').value);

    const payload = { email, full_name, phone, role_id };
    if (password) payload.password = password;

    const res = await fetchWithAuth(`${API_BASE}/users/detail/${username}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload),
    });

    if (res.ok) {
        showNotification('Пользователь обновлён');
        bootstrap.Modal.getInstance(document.getElementById('editUserModal')).hide();
        loadUsers();
    } else {
        const err = await res.json();
        showNotification(err.message || 'Ошибка при обновлении');
    }
};
