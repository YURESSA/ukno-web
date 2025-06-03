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
