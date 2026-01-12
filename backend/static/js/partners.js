let currentPartnerId = null;
let selectedPartnerPhoto = null;

const partnerModalEl = document.getElementById('partnerModal');
const partnerModal = new bootstrap.Modal(partnerModalEl);

async function loadPartnersSection() {
    showCreateButton(true, 'partners');

    const res = await fetchWithAuth(`${API_REF_BASE}/partners`);
    if (!res) return;

    const data = await res.json();

    const rows = data.map(item => ({
        id: item.id,
        cells: [
            item.id,
            item.name,
            item.link || '—',
            item.order_index,
            item.photo ? `<img src="${location.origin}/${item.photo}" width="50"/>` : '—'
        ],
        actions: `
            <button class="btn btn-outline-danger btn-sm btn-delete-partner" data-id="${item.id}">
                <i class="fas fa-trash"></i> Удалить
            </button>
        `
    }));

    renderTable(
        'Партнёры',
        ['ID', 'Название', 'Ссылка', 'Порядок', 'Фото'],
        rows
    );

    document.querySelectorAll('#excursionsTable tbody tr').forEach(row => {
        row.onclick = async (e) => {
            if (e.target.closest('button')) return;
            const id = row.dataset.id;
            if (!id) return;

            const res = await fetchWithAuth(`${API_REF_BASE}/partners/${id}`);
            if (!res) {
                showNotification('Ошибка загрузки партнёра', 'danger');
                return;
            }

            const data = await res.json();
            showPartnerModal(data);
        };
    });

    document.querySelectorAll('.btn-delete-partner').forEach(btn => {
        btn.onclick = async (e) => {
            e.stopPropagation();
            const id = btn.dataset.id;
            if (!confirm('Удалить партнёра?')) return;

            const res = await fetchWithAuth(`${API_REF_BASE}/partners/${id}`, {
                method: 'DELETE'
            });

            if (res.ok) {
                showNotification('Партнёр удалён', 'success');
                loadPartnersSection();
            } else {
                showNotification('Ошибка удаления', 'danger');
            }
        };
    });
}

function showPartnerModal(item) {
    currentPartnerId = item?.id || null;
    selectedPartnerPhoto = null;

    document.getElementById('partnerName').value = item?.name || '';
    document.getElementById('partnerLink').value = item?.link || '';
    document.getElementById('partnerOrder').value = item?.order_index ?? 0;
    document.getElementById('partnerPhotoUpload').value = '';

    const container = document.getElementById('partnerPhotoPreview');
    container.innerHTML = '';

    if (item?.photo) {
        addPartnerPhotoPreview(container, item.photo, true);
    }

    partnerModal.show();
}

function addPartnerPhotoPreview(container, photoPathOrFile, uploaded = false) {
    const wrapper = document.createElement('div');
    wrapper.style.position = 'relative';
    wrapper.style.display = 'inline-block';
    wrapper.style.margin = '5px';

    const img = document.createElement('img');
    img.style.width = '150px';
    img.style.borderRadius = '4px';
    img.src = uploaded
        ? `${location.origin}/${photoPathOrFile}`
        : URL.createObjectURL(photoPathOrFile);

    wrapper.appendChild(img);

    const delBtn = document.createElement('button');
    delBtn.textContent = '×';
    delBtn.title = 'Удалить фото';
    delBtn.style.position = 'absolute';
    delBtn.style.top = '5px';
    delBtn.style.right = '5px';
    delBtn.style.background = 'rgba(255,0,0,0.7)';
    delBtn.style.border = 'none';
    delBtn.style.color = 'white';
    delBtn.style.fontWeight = 'bold';
    delBtn.style.borderRadius = '50%';
    delBtn.style.cursor = 'pointer';

    delBtn.onclick = async () => {
    if (!confirm('Удалить фото?')) return;

    if (uploaded) {
        const res = await fetchWithAuth(
            `${API_REF_BASE}/partners/${currentPartnerId}/photo`,
            { method: 'DELETE' }
        );

        if (!res) {
            showNotification('Ошибка при удалении фото', 'danger');
            return;
        }

        if (res.ok) {
            showNotification('Фото удалено', 'success');
            wrapper.remove();
        } else {
            showNotification('Ошибка при удалении фото', 'danger');
        }
    } else {
        selectedPartnerPhoto = null;
        wrapper.remove();
        document.getElementById('partnerPhotoUpload').value = '';
    }
};


    wrapper.appendChild(delBtn);
    container.appendChild(wrapper);
}

document.getElementById('partnerPhotoUpload').addEventListener('change', (e) => {
    if (!e.target.files.length) return;

    selectedPartnerPhoto = e.target.files[0];
    const container = document.getElementById('partnerPhotoPreview');
    container.innerHTML = '';
});

document.getElementById('btnUploadPartnerPhoto').addEventListener('click', async () => {
    if (!currentPartnerId) {
        showNotification('Сначала выберите партнёра', 'warning');
        return;
    }

    if (!selectedPartnerPhoto) {
        showNotification('Выберите фото', 'warning');
        return;
    }

    const formData = new FormData();
    formData.append('photo', selectedPartnerPhoto);

    const res = await fetchWithAuth(
        `${API_REF_BASE}/partners/${currentPartnerId}/photo`,
        { method: 'POST', body: formData }
    );

    if (res.ok) {
        const data = await res.json();
        showNotification('Фото загружено', 'success');

        const container = document.getElementById('partnerPhotoPreview');
        container.innerHTML = '';
        addPartnerPhotoPreview(container, data.photo_path, true);

        selectedPartnerPhoto = null;
        document.getElementById('partnerPhotoUpload').value = '';
    } else {
        showNotification('Ошибка загрузки фото', 'danger');
    }
});

document.getElementById('partnerSaveBtn').addEventListener('click', async () => {
    const name = document.getElementById('partnerName').value.trim();
    const link = document.getElementById('partnerLink').value.trim();
    const orderIndex = parseInt(document.getElementById('partnerOrder').value) || 0;

    const formData = new FormData();
    formData.append('name', name);
    formData.append('link', link);
    formData.append('order_index', orderIndex);

    if (selectedPartnerPhoto) {
        formData.append('photo', selectedPartnerPhoto);
    }

    let res;
    if (!currentPartnerId) {
        res = await fetchWithAuth(`${API_REF_BASE}/partners`, {
            method: 'POST',
            body: formData
        });
    } else {
        res = await fetchWithAuth(`${API_REF_BASE}/partners/${currentPartnerId}`, {
            method: 'PUT',
            body: formData
        });
    }

    if (res.ok) {
        showNotification('Партнёр сохранён', 'success');
        await loadPartnersSection();
        partnerModal.hide();
    } else {
        const err = await res.json();
        showNotification(err.message || 'Ошибка сохранения', 'danger');
    }
});

partnerModalEl.addEventListener('hidden.bs.modal', () => {
    currentPartnerId = null;
    selectedPartnerPhoto = null;

    document.getElementById('partnerName').value = '';
    document.getElementById('partnerLink').value = '';
    document.getElementById('partnerOrder').value = '';
    document.getElementById('partnerPhotoUpload').value = '';
    document.getElementById('partnerPhotoPreview').innerHTML = '';
});

document.getElementById('btnCreatePartner').addEventListener('click', () => showPartnerModal(null));
