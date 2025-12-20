let currentCulturalId = null;
let selectedCulturalPhoto = null;
const culturalModalEl = document.getElementById('culturalSpaceModal');
const culturalModal = new bootstrap.Modal(culturalModalEl);

// Загрузка списка элементов культурного пространства
async function loadHomeSection() {
    showCreateButton(true, 'cultural-space'); // кнопка "Добавить элемент"
    const res = await fetchWithAuth(`${API_REF_BASE}/cultural-space`);
    if (!res) return;
    const data = await res.json();

    const rows = data.map(item => ({
        id: item.id,

        cells: [item.id, item.text, item.order_index, item.photo ? `<img src="${location.origin}/${item.photo}" width="50"/>` : '—'],
        actions: `
            <button class="btn btn-outline-danger btn-sm btn-delete-cultural" data-id="${item.id}">
                <i class="fas fa-trash"></i> Удалить
            </button>
        `
    }));

    renderTable('Культурное пространство', ['ID', 'Текст', 'Порядок', 'Фото'], rows);

    document.querySelectorAll('#excursionsTable tbody tr').forEach(row => {
        row.onclick = async (e) => {
            if (e.target.closest('button')) return;
            const id = row.dataset.id;
            if (!id) return;
            const res = await fetchWithAuth(`${API_REF_BASE}/cultural-space/${id}`);
            if (!res) {
                showNotification('Ошибка загрузки элемента', 'danger');
                return;
            }
            const data = await res.json();
            showCulturalModal(data);
        };
    });

    document.querySelectorAll('.btn-delete-cultural').forEach(btn => {
        btn.onclick = async (e) => {
            e.stopPropagation();
            const id = btn.dataset.id;
            if (!confirm('Удалить элемент?')) return;
            const res = await fetchWithAuth(`${API_REF_BASE}/cultural-space/${id}`, {method: 'DELETE'});
            if (res.ok) {
                showNotification('Элемент удалён', 'success');
                loadHomeSection();
            } else {
                showNotification('Ошибка удаления', 'danger');
            }
        };
    });
}

// Показ модалки
function showCulturalModal(item) {
    currentCulturalId = item?.id || null;
    selectedCulturalPhoto = null;

    document.getElementById('culturalSpaceText').value = item?.text || '';
    document.getElementById('culturalSpaceOrder').value = item?.order_index ?? 0;
    document.getElementById('culturalSpacePhotoUpload').value = '';
    const container = document.getElementById('culturalSpacePhotoPreview');
    container.innerHTML = '';

    if (item?.photo) {
        addCulturalPhotoPreview(container, item.photo, true);
    }

    culturalModal.show();
}

// Добавление фото в превью
function addCulturalPhotoPreview(container, photoPathOrFile, uploaded = false) {
    const wrapper = document.createElement('div');
    wrapper.style.position = 'relative';
    wrapper.style.display = 'inline-block';
    wrapper.style.margin = '5px';

    const img = document.createElement('img');
    img.style.width = '150px';
    img.style.borderRadius = '4px';
    img.src = uploaded ? `${location.origin}/${photoPathOrFile}` : URL.createObjectURL(photoPathOrFile);
    wrapper.appendChild(img);

    const delBtn = document.createElement('button');
    delBtn.textContent = '×';
    delBtn.title = 'Удалить фото';
    delBtn.style.position = 'absolute';
    delBtn.style.top = '5px';
    delBtn.style.right = '5px';
    delBtn.style.backgroundColor = 'rgba(255,0,0,0.7)';
    delBtn.style.border = 'none';
    delBtn.style.color = 'white';
    delBtn.style.fontWeight = 'bold';
    delBtn.style.borderRadius = '50%';
    delBtn.style.cursor = 'pointer';
    delBtn.onclick = async () => {
        if (!confirm('Удалить фото?')) return;

        if (uploaded) {
            const res = await fetchWithAuth(`${API_REF_BASE}/cultural-space/${currentCulturalId}/photo`, {method: 'DELETE'});
            if (res.ok) {
                showNotification('Фото удалено', 'success');
                wrapper.remove();
            } else {
                showNotification('Ошибка при удалении фото', 'danger');
            }
        } else {
            selectedCulturalPhoto = null;
            wrapper.remove();
            document.getElementById('culturalSpacePhotoUpload').value = '';
        }
    };

    wrapper.appendChild(delBtn);
    container.appendChild(wrapper);
}

// Выбор локального фото (только превью)
document.getElementById('culturalSpacePhotoUpload').addEventListener('change', (e) => {
    if (!e.target.files.length) return;
    selectedCulturalPhoto = e.target.files[0];

    const container = document.getElementById('culturalSpacePhotoPreview');
    container.innerHTML = '';
});

// Загрузка выбранного фото на сервер
document.getElementById('btnUploadCulturalSpacePhoto').addEventListener('click', async () => {
    if (!currentCulturalId) {
        showNotification('Сначала выберите элемент', 'warning');
        return;
    }
    if (!selectedCulturalPhoto) {
        showNotification('Выберите фото для загрузки', 'warning');
        return;
    }

    const formData = new FormData();
    formData.append('photo', selectedCulturalPhoto);

    const res = await fetchWithAuth(`${API_REF_BASE}/cultural-space/${currentCulturalId}/photo`, {
        method: 'POST',
        body: formData
    });

    if (res.ok) {
        const data = await res.json();
        showNotification('Фото загружено', 'success');
        const container = document.getElementById('culturalSpacePhotoPreview');
        container.innerHTML = '';
        addCulturalPhotoPreview(container, data.photo_path, true);
        selectedCulturalPhoto = null;
        document.getElementById('culturalSpacePhotoUpload').value = '';
    } else {
        showNotification('Ошибка загрузки фото', 'danger');
    }
});

// Сохранение элемента культурного пространства
document.getElementById('culturalSpaceSaveBtn').addEventListener('click', async () => {
    const text = document.getElementById('culturalSpaceText').value.trim();
    const orderIndex = parseInt(document.getElementById('culturalSpaceOrder').value) || 0;
    const photoInput = document.getElementById('culturalSpacePhotoUpload');

    const formData = new FormData();
    formData.append('text', text);
    formData.append('order_index', orderIndex);
    if (photoInput.files.length > 0) formData.append('photo', photoInput.files[0]);

    try {
        let res;
        if (!currentCulturalId) {
            res = await fetchWithAuth(`${API_REF_BASE}/cultural-space`, {method: 'POST', body: formData});
        } else {
            res = await fetchWithAuth(`${API_REF_BASE}/cultural-space/${currentCulturalId}`, {
                method: 'PUT',
                body: formData
            });
        }

        if (res.ok) {
            showNotification('Элемент сохранён', 'success');
            await loadHomeSection();
            culturalModal.hide();
        } else {
            const err = await res.json();
            showNotification(err.message || 'Ошибка сохранения', 'danger');
        }
    } catch (e) {
        console.error(e);
        showNotification('Ошибка сети', 'danger');
    }
});

// Очистка модалки при закрытии
culturalModalEl.addEventListener('hidden.bs.modal', () => {
    currentCulturalId = null;
    selectedCulturalPhoto = null;
    document.getElementById('culturalSpaceText').value = '';
    document.getElementById('culturalSpacePhotoUpload').value = '';
    document.getElementById('culturalSpacePhotoPreview').innerHTML = '';
    document.getElementById('culturalSpaceOrder').value = '';
});

// Создание нового элемента
document.getElementById('btnCreateCulturalSpace').addEventListener('click', () => showCulturalModal(null));
