const urlMap = {
    'categories': `${API_REF_BASE}/categories`,
    'format-types': `${API_REF_BASE}/format-types`,
    'age-categories': `${API_REF_BASE}/age-categories`,
    'roles': `${API_REF_BASE}/roles`,
};

const titles = {
    'categories': 'Категории',
    'format-types': 'Типы форматов',
    'age-categories': 'Возрастные категории',
    'roles': 'Роли Пользователей',
};

const idFields = {
    'categories': 'category_id',
    'format-types': 'format_type_id',
    'age-categories': 'age_category_id',
    'roles': 'role_id'
};

const nameFields = {
    'categories': 'category_name',
    'format-types': 'format_type_name',
    'age-categories': 'age_category_name',
    'roles': 'role_name'
};

let currentRef = null;

const modal = new bootstrap.Modal(document.getElementById('createRefModal'));

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
      <button class="btn btn-outline-danger btn-sm btn-delete-ref" data-ref="${refName}" data-id="${item[idFields[refName]]}">
          <i class="fas fa-trash me-1"></i> Удалить
        </button>
`
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
        modal.hide();
        loadReference(currentRef);
    }
};

document.getElementById('btnCreateRef').onclick = () => {
    if (!currentRef) {
        showNotification('Сначала выберите раздел справочника');
        return;
    }
    // Очистить поле ввода
    document.getElementById('refNameInput').value = '';
    // Показать модалку

    modal.show();
};