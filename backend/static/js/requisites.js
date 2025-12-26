// =======================
// Загрузка списка реквизитов
// =======================
async function loadRequisitesSection() {
    showCreateButton(true, 'requisites');

    const res = await fetchWithAuth(`${API_REF_BASE}/requisites`);
    if (!res) return;
    const data = await res.json();

    const rows = data.map(item => ({
        id: item.id,
        cells: [
            item.id,
            item.title,
            item.file ? `<a href="${location.origin}/${item.file}" target="_blank">Скачать</a>` : '—'
        ],
        actions: `
            <button class="btn btn-outline-danger btn-sm btn-delete-requisite" data-id="${item.id}">
                Удалить
            </button>
        `
    }));

    renderTable('Реквизиты', ['ID', 'Название', 'Файл'], rows);

    // Клик по строке для редактирования
    document.querySelectorAll('#excursionsTable tbody tr').forEach(row => {
        row.onclick = async (e) => {
            if (e.target.closest('button')) return;
            const id = row.dataset.id;
            if (!id) return;
            const res = await fetchWithAuth(`${API_REF_BASE}/requisites/${id}`);
            if (!res) return showNotification('Ошибка загрузки реквизита', 'danger');
            const data = await res.json();
            showRequisiteModal(data);
        };
    });

    // Удаление реквизита
    document.querySelectorAll('.btn-delete-requisite').forEach(btn => {
        btn.onclick = async (e) => {
            e.stopPropagation();
            const id = btn.dataset.id;
            if (!confirm('Удалить реквизит?')) return;

            const res = await fetchWithAuth(`${API_REF_BASE}/requisites/${id}`, { method: 'DELETE' });
            if (res && res.ok) {
                showNotification('Реквизит удалён', 'success');
                loadRequisitesSection();
            } else {
                showNotification('Ошибка удаления', 'danger');
            }
        };
    });
}

let currentRequisiteId = null;
let selectedRequisiteFile = null;
const requisiteModalEl = document.getElementById('requisiteModal');
const requisiteModal = new bootstrap.Modal(requisiteModalEl);

// =======================
// Функция для добавления превью файла с кнопкой удаления
// =======================
function addRequisiteFilePreview(container, filePath) {
    container.innerHTML = '';

    const link = document.createElement('a');
    link.href = `${location.origin}/${filePath}`;
    link.target = '_blank';
    link.textContent = filePath.split('/').pop();
    container.appendChild(link);

    const delBtn = document.createElement('button');
    delBtn.className = 'btn btn-sm btn-outline-danger ms-2';
    delBtn.textContent = 'Удалить';
    delBtn.onclick = async () => {
        if (!confirm('Удалить файл?')) return;

        const res = await fetchWithAuth(`${API_REF_BASE}/requisites/${currentRequisiteId}/file`, { method: 'DELETE' });
        if (res && res.ok) {
            showNotification('Файл удалён', 'success');
            container.innerHTML = '';
        } else {
            showNotification('Ошибка при удалении файла', 'danger');
        }
    };
    container.appendChild(delBtn);
}

// =======================
// Показ модалки
// =======================
function showRequisiteModal(item) {
    currentRequisiteId = item?.id || null;
    selectedRequisiteFile = null;

    document.getElementById('requisiteTitle').value = item?.title || '';
    document.getElementById('requisiteFileUpload').value = '';
    const container = document.getElementById('requisiteFilePreview');

    if (item?.file) {
        addRequisiteFilePreview(container, item.file);
    } else {
        container.innerHTML = '';
    }

    requisiteModal.show();
}

// =======================
// Выбор локального файла
// =======================
document.getElementById('requisiteFileUpload').addEventListener('change', (e) => {
    if (!e.target.files.length) return;
    selectedRequisiteFile = e.target.files[0];
});

// =======================
// Загрузка файла на сервер
// =======================
document.getElementById('btnUploadRequisiteFile').addEventListener('click', async () => {
    if (!currentRequisiteId) return showNotification('Сначала выберите реквизит', 'warning');
    if (!selectedRequisiteFile) return showNotification('Выберите файл для загрузки', 'warning');

    const formData = new FormData();
    formData.append('file', selectedRequisiteFile);

    const res = await fetchWithAuth(`${API_REF_BASE}/requisites/${currentRequisiteId}/file`, {
        method: 'POST',
        body: formData
    });

    if (res && res.ok) {
        const data = await res.json();
        showNotification('Файл загружен', 'success');
        addRequisiteFilePreview(document.getElementById('requisiteFilePreview'), data.file_path);
        selectedRequisiteFile = null;
        document.getElementById('requisiteFileUpload').value = '';
    } else {
        showNotification('Ошибка загрузки файла', 'danger');
    }
});

// =======================
// Сохранение реквизита
// =======================
document.getElementById('requisiteSaveBtn').addEventListener('click', async () => {
    const title = document.getElementById('requisiteTitle').value.trim();
    const fileInput = document.getElementById('requisiteFileUpload');

    if (!title) return showNotification('Введите название', 'warning');

    const formData = new FormData();
    formData.append('title', title);
    if (fileInput.files.length > 0) formData.append('file', fileInput.files[0]);

    let res;
    if (!currentRequisiteId) {
        res = await fetchWithAuth(`${API_REF_BASE}/requisites`, { method: 'POST', body: formData });
    } else {
        res = await fetchWithAuth(`${API_REF_BASE}/requisites/${currentRequisiteId}`, { method: 'PUT', body: formData });
    }

    if (res && res.ok) {
        showNotification('Реквизит сохранён', 'success');
        await loadRequisitesSection();
        requisiteModal.hide();
    } else {
        const err = await res.json();
        showNotification(err.message || 'Ошибка сохранения', 'danger');
    }
});

// =======================
// Очистка модалки при закрытии
// =======================
requisiteModalEl.addEventListener('hidden.bs.modal', () => {
    currentRequisiteId = null;
    selectedRequisiteFile = null;
    document.getElementById('requisiteTitle').value = '';
    document.getElementById('requisiteFileUpload').value = '';
    document.getElementById('requisiteFilePreview').innerHTML = '';
});

// =======================
// Кнопка создания нового реквизита
// =======================
const btnCreate = document.getElementById('btnCreateRequisite');
if (btnCreate) {
    btnCreate.addEventListener('click', () => showRequisiteModal(null));
}
