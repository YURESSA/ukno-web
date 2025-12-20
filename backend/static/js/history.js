let currentHistoryId = null;
const historyModalEl = document.getElementById('historyModal');
const historyModal = new bootstrap.Modal(historyModalEl);

// Загрузка списка событий истории
async function loadHistorySection() {
    showCreateButton(true, 'history'); // показать кнопку "Добавить событие"
    const res = await fetchWithAuth(`${API_REF_BASE}/history`);
    if (!res) return;
    const data = await res.json();
    const rows = data.map(item => ({
        id: item.id,
        cells: [
            item.id,
            item.title,
            item.date,
            item.link,
            item.description
        ],
        actions: `
        <button class="btn btn-outline-danger btn-sm btn-delete-history" data-id="${item.id}">
            <i class="fas fa-trash"></i> Удалить
        </button>
    `
    }));

    renderTable(
        'История компании',
        ['ID', 'Название', 'Дата', 'Ссылка', 'Описание'],
        rows
    );

    document.querySelectorAll('#excursionsTable tbody tr').forEach(row => {
        row.onclick = async (e) => {
            if (e.target.closest('button')) return;
            const id = row.dataset.id;
            if (!id) return;
            const res = await fetchWithAuth(`${API_REF_BASE}/history/${id}`);
            if (!res) {
                showNotification('Ошибка загрузки события', 'danger');
                return;
            }
            const data = await res.json();
            showHistoryModal(data);
        };
    });

    document.querySelectorAll('.btn-delete-history').forEach(btn => {
        btn.onclick = async (e) => {
            e.stopPropagation();
            const id = btn.dataset.id;
            if (!confirm('Удалить событие?')) return;
            const res = await fetchWithAuth(`${API_REF_BASE}/history/${id}`, {method: 'DELETE'});
            if (res.ok) {
                showNotification('Событие удалено', 'success');
                loadHistorySection();
            } else {
                showNotification('Ошибка удаления', 'danger');
            }
        };
    });
}

// Показ модалки события
function showHistoryModal(item) {
    currentHistoryId = item?.id || null;
    document.getElementById('historyTitle').value = item?.title || '';
    document.getElementById('historyDate').value = item?.date || '';
    document.getElementById('historyLink').value = item?.link || '';
    document.getElementById('historyDescription').value = item?.description || '';
    historyModal.show();
}

// Сохранение события (создание/обновление)
document.getElementById('historySaveBtn').addEventListener('click', async () => {
    const title = document.getElementById('historyTitle').value.trim(); // ←
    const date = document.getElementById('historyDate').value;
    const link = document.getElementById('historyLink').value.trim();
    const description = document.getElementById('historyDescription').value.trim();

    if (!title || !date || !link || !description) {
        showNotification('Заполните все поля', 'warning');
        return;
    }

    try {
        const body = JSON.stringify({title, date, link, description}); // ←
        const options = {
            method: currentHistoryId ? 'PUT' : 'POST',
            headers: {'Content-Type': 'application/json'},
            body
        };

        const url = currentHistoryId
            ? `${API_REF_BASE}/history/${currentHistoryId}`
            : `${API_REF_BASE}/history`;

        const res = await fetchWithAuth(url, options);

        if (res.ok) {
            showNotification('Событие сохранено', 'success');
            await loadHistorySection();
            historyModal.hide();
        } else {
            const err = await res.json();
            showNotification(err.message || 'Ошибка сохранения', 'danger');
        }
    } catch (e) {
        console.error(e);
        showNotification('Ошибка сети', 'danger');
    }
});


historyModalEl.addEventListener('hidden.bs.modal', () => {
    currentHistoryId = null;
    document.getElementById('historyTitle').value = '';
    document.getElementById('historyDate').value = '';
    document.getElementById('historyLink').value = '';
    document.getElementById('historyDescription').value = '';
});


document.getElementById('btnCreateHistory').addEventListener('click', () => showHistoryModal(null));
