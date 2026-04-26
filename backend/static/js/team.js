let currentTeamMemberId = null;
let selectedTeamPhoto = null; // выбранное фото, но ещё не загруженное
const teamModalEl = document.getElementById('teamModal');
const teamModal = new bootstrap.Modal(teamModalEl);

async function loadTeamSection() {
    showCreateButton(true, 'team');
    const res = await fetchWithAuth(`${API_REF_BASE}/team`);
    if (!res) return;
    const data = await res.json();

    const rows = data.map(member => ({
        id: member.id,
        cells: [
            member.id,
            member.full_name,
            member.description || '—',
            member.photo ? `<img src="${location.origin}/${member.photo}" width="50" style="border-radius:4px;"/>` : '—'
        ],
        actions: `
            <button class="btn btn-outline-danger btn-sm btn-delete-team" data-id="${member.id}">
                <i class="fas fa-trash"></i> Удалить
            </button>
        `
    }));

    renderTable('Команда', ['ID', 'ФИО', 'Описание', 'Фото'], rows);

    document.querySelectorAll('#excursionsTable tbody tr').forEach(row => {
        row.onclick = async (e) => {
            if (e.target.closest('button')) return;
            const id = row.dataset.id;
            if (!id) return;
            const res = await fetchWithAuth(`${API_REF_BASE}/team/${id}`);
            if (!res) {
                showNotification('Ошибка загрузки сотрудника', 'danger');
                return;
            }
            const data = await res.json();
            showTeamModal(data);
        };
    });

    document.querySelectorAll('.btn-delete-team').forEach(btn => {
        btn.onclick = async (e) => {
            e.stopPropagation();
            const id = btn.dataset.id;
            if (!confirm('Удалить сотрудника?')) return;
            const res = await fetchWithAuth(`${API_REF_BASE}/team/${id}`, {method: 'DELETE'});
            if (res.ok) {
                showNotification('Сотрудник удалён', 'success');
                loadTeamSection();
            } else {
                showNotification('Ошибка удаления', 'danger');
            }
        };
    });
}

function showTeamModal(member) {
    currentTeamMemberId = member?.id || null;
    selectedTeamPhoto = null;

    document.getElementById('teamFullName').value = member?.full_name || '';
    document.getElementById('teamDescription').value = member?.description || '';
    document.getElementById('teamPhotoUpload').value = '';
    const container = document.getElementById('teamPhotoPreview');
    container.innerHTML = '';

    if (member?.photo) {
        addPhotoPreview(container, member.photo, true);
    }

    teamModal.show();
}

// Добавляем фото в превью (uploaded: true — фото с сервера, false — локально выбранное)
function addPhotoPreview(container, photoPathOrFile, uploaded = false) {
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
            // Фото с сервера
            const res = await fetchWithAuth(`${API_REF_BASE}/team/${currentTeamMemberId}/photo`, {method: 'DELETE'});
            if (res.ok) {
                showNotification('Фото удалено', 'success');
                wrapper.remove();
            } else {
                showNotification('Ошибка при удалении фото', 'danger');
            }
        } else {
            // Локально выбранное фото
            selectedTeamPhoto = null;
            wrapper.remove();
            document.getElementById('teamPhotoUpload').value = '';
        }
    };

    wrapper.appendChild(delBtn);
    container.appendChild(wrapper);
}

// Выбор фото (только отображаем превью, не загружаем)
document.getElementById('teamPhotoUpload').addEventListener('change', (e) => {
    if (!e.target.files.length) return;
    selectedTeamPhoto = e.target.files[0];

    const container = document.getElementById('teamPhotoPreview');
    container.innerHTML = '';
});

// Загрузка выбранного фото
document.getElementById('btnUploadTeamPhoto').addEventListener('click', async () => {
    if (!currentTeamMemberId) {
        showNotification('Сначала выберите сотрудника', 'warning');
        return;
    }
    if (!selectedTeamPhoto) {
        showNotification('Выберите фото для загрузки', 'warning');
        return;
    }

    const formData = new FormData();
    formData.append('photo', selectedTeamPhoto);

    const res = await fetchWithAuth(`${API_REF_BASE}/team/${currentTeamMemberId}/photo`, {
        method: 'POST',
        body: formData
    });

    if (res.ok) {
        const data = await res.json();
        showNotification('Фото загружено', 'success');
        const container = document.getElementById('teamPhotoPreview');
        container.innerHTML = '';
        addPhotoPreview(container, data.photo_path, true);
        selectedTeamPhoto = null;
        document.getElementById('teamPhotoUpload').value = '';
    } else {
        showNotification('Ошибка загрузки фото', 'danger');
    }
});

// Сохранение данных сотрудника (без фото)
document.getElementById('teamSaveBtn').addEventListener('click', async () => {
    const fullName = document.getElementById('teamFullName').value.trim();
    const description = document.getElementById('teamDescription').value.trim();
    const photoInput = document.getElementById('teamPhotoUpload');
    const formData = new FormData();
    formData.append('full_name', fullName);
    formData.append('description', description);
    if (photoInput.files.length > 0) formData.append('photo', photoInput.files[0]);

    try {
        let res;
        if (!currentTeamMemberId) {
            res = await fetchWithAuth(`${API_REF_BASE}/team`, {method: 'POST', body: formData});
        } else {
            res = await fetchWithAuth(`${API_REF_BASE}/team/${currentTeamMemberId}`, {method: 'PUT', body: formData});
        }
        if (res.ok) {
            showNotification('Сотрудник сохранён', 'success');
            await loadTeamSection();
            teamModal.hide();
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
teamModalEl.addEventListener('hidden.bs.modal', () => {
    currentTeamMemberId = null;
    selectedTeamPhoto = null;
    document.getElementById('teamFullName').value = '';
    document.getElementById('teamDescription').value = '';
    document.getElementById('teamPhotoUpload').value = '';
    document.getElementById('teamPhotoPreview').innerHTML = '';
});

// Создание нового сотрудника
document.getElementById('btnCreateTeam').addEventListener('click', () => showTeamModal(null));
