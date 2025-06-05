let currentExcursionId = null;
let originalExcursionData = {};
const photoInput = document.getElementById('modalPhotoUpload');
const btnAddPhoto = document.getElementById('btnAddPhoto')

// Получаем элементы
const excursionModalEl = document.getElementById('excursionModal');
const sessionModalEl = document.getElementById('sessionModal');

// Создаём экземпляры Bootstrap.Modal
const excursionModal = new bootstrap.Modal(excursionModalEl);
const sessionModal = new bootstrap.Modal(sessionModalEl);

// Чтобы при закрытии sessionModal автоматически снова открывать excursionModal:
sessionModalEl.addEventListener('hidden.bs.modal', () => {
    excursionModal.show();
});

document.querySelector('#sessionModal .btn-close').addEventListener('click', () => {
    sessionModal.hide();
});


async function loadExcursions() {
    showCreateButton(true, 'excursion');
    const res = await fetchWithAuth(`${API_BASE}/excursions`);
    if (!res) return;
    const data = await res.json();

    const rows = data.excursions.map(item => ({
        id: item.excursion_id,  // добавляем id
        cells: [
            item.excursion_id,
            item.title,
            (item.description ? item.description.slice(0, 100) + '...' : ''),
            item.category?.category_name || '',
            item.format_type?.format_type_name || '',
            item.age_category?.age_category_name || '',
        ],
        actions: `
          <button class="btn btn-outline-danger btn-sm btn-delete-excursion" data-id="${item.excursion_id}">
            <i class="fas fa-trash"></i> Удалить
          </button>
        `
    }));

    renderTable('События', ['ID', 'Название', 'Описание', 'Категория', 'Формат', 'Возраст'], rows);

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

    excursionModal.show()

}

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

function openSessionModalForEdit(session) {
    excursionModal.hide()
    document.getElementById('editingSessionId').value = session.session_id;
    document.getElementById('sessionDatetimeModal').value = session.start_datetime.slice(0, 16);
    document.getElementById('sessionCostModal').value = session.cost;
    document.getElementById('sessionMaxParticipantsModal').value = session.max_participants;
    sessionModal.show();
}

async function deleteSession(sessionId) {
    if (!confirm('Удалить сессию?')) return;

    // Удаление временной сессии (которая ещё не была сохранена на сервере)
    if (String(sessionId).startsWith('temp_')) {
        originalExcursionData.sessions = originalExcursionData.sessions.filter(s => String(s.session_id) !== String(sessionId));
        console.log(originalExcursionData.sessions)
        renderSessions(originalExcursionData.sessions);
        showNotification('Сессия удалена (не сохранена)', 'success');
        return;
    }


    // Защита от удаления до создания экскурсии
    if (!currentExcursionId || !sessionId) {
        showNotification('Нельзя удалить сессию до создания экскурсии', 'warning');
        return;
    }

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


function excursionPhotosRender(photos) {
    const photosDiv = document.getElementById('modalPhotos');
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
        p.textContent = `${date.toLocaleString()} — Стоимость: ${s.cost} руб, Участников: ${s.booked ?? 0}/${s.max_participants}`;

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


document.getElementById('modalSave').onclick = async () => {
    const isNew = !currentExcursionId;

    // Собираем данные экскурсии в объект
    const excursionData = collectExcursionFormData();

    if (isNew) {
        // Создаем formData для отправки multipart/form-data
        const formData = new FormData();

        // Кладём данные экскурсии в поле 'data' в виде JSON-строки
        formData.append('data', JSON.stringify(excursionData));

        // Кладём фотографии (если есть)
        const photosInput = photoInput; // предположим, что input для фото с таким id
        if (photosInput && photosInput.files.length > 0) {
            for (const file of photosInput.files) {
                formData.append('photos', file);
            }
        }

        try {
            const res = await fetchWithAuth(`${API_BASE}/excursions`, {
                method: 'POST',
                body: formData,
            });

            if (!res.ok) {
                const errorData = await res.json();
                showNotification(errorData.message || 'Ошибка создания экскурсии', 'danger');
                return;
            }

            const data = await res.json();
            showNotification('Экскурсия успешно создана', 'success');

            currentExcursionId = data.excursion_id || data.id || null;
            originalExcursionData = {...excursionData, ...data};

            loadExcursions();
            excursionModal.hide()

        } catch (e) {
            showNotification('Ошибка сети при создании экскурсии', 'danger');
        }

    } else {
        // Для обновления существующей экскурсии — как в вашем текущем коде, отправляем JSON, если API это поддерживает
        // Или сделать аналогично с FormData, если нужно тоже отправлять фото/сессии.
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
            excursionModal.hide()
            document.getElementById('excursionModal').style.display = 'none';
        } catch (e) {
            showNotification('Ошибка сети', 'danger');
        }
    }
};

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
        photoInput.value = '';
        excursionPhotosRender(data.photos);
    } catch (e) {
        console.log(e)
        showNotification('Ошибка сети при загрузке фото', 'danger');
    }
};

document.getElementById('saveSessionModalBtn').addEventListener('click', async () => {
    const sessionId = document.getElementById('editingSessionId').value;
    const datetime = document.getElementById('sessionDatetimeModal').value;
    const cost = document.getElementById('sessionCostModal').value;
    const maxParticipants = document.getElementById('sessionMaxParticipantsModal').value;

    if (!datetime || !cost || !maxParticipants) {
        showNotification('Заполните все поля', 'warning');
        return;
    }

    const sessionData = {
        start_datetime: new Date(datetime).toISOString(),
        cost: Number(cost),
        max_participants: Number(maxParticipants),
    };

    if (currentExcursionId === null) {
        // Экскурсия еще не создана, просто обновляем локальные данные сессий
        if (sessionId) {
            // редактируем существующую сессию в originalExcursionData.sessions
            const sessionIndex = originalExcursionData.sessions.findIndex(s => s.id === sessionId);
            if (sessionIndex !== -1) {
                originalExcursionData.sessions[sessionIndex] = {...originalExcursionData.sessions[sessionIndex], ...sessionData};
            }
        } else {
            // создаём временный ID для новой сессии, например отрицательный или строковый
            const tempId = 'temp_' + Date.now();
            if (!originalExcursionData.sessions) {
                originalExcursionData.sessions = [];
            }
            originalExcursionData.sessions.push({...sessionData, session_id: tempId});
        }
        renderSessions(originalExcursionData.sessions);
        showNotification('Сессия добавлена', 'success');
        sessionModal.hide();
        return;
    }

    // Если экскурсия уже создана, делаем запросы к API

    const method = sessionId ? 'PATCH' : 'POST';
    const url = sessionId
        ? `/api/admin/excursions/${currentExcursionId}/sessions/${sessionId}`
        : `/api/admin/excursions/${currentExcursionId}/sessions`;

    try {
        const res = await fetchWithAuth(url, {
            method,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(sessionData),
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
        sessionModal.hide();
    } catch (err) {
        showNotification('Ошибка: ' + err.message, 'danger');
    }
});


document.getElementById('btnCreateExcurs').onclick = () => {
    currentExcursionId = null;
    originalExcursionData = {};

    // Очистить все поля модалки
    document.getElementById('modalTitle').value = '';
    document.getElementById('modalDescription').value = '';
    document.getElementById('modalCategory').value = '';
    document.getElementById('modalFormat').value = '';
    document.getElementById('modalAgeCategory').value = '';
    document.getElementById('modalDuration').value = '';
    document.getElementById('modalPlace').value = '';
    document.getElementById('modalConductedBy').value = '';
    document.getElementById('modalWorkingHours').value = '';
    document.getElementById('modalContactEmail').value = '';
    document.getElementById('modalTelegram').value = '';
    document.getElementById('modalVk').value = '';
    document.getElementById('modalIsActive').value = 'true';
    document.getElementById('modalDistance').value = '';
    document.getElementById('modalTimeToStop').value = '';
    document.getElementById('modalIframe').value = '';

    document.getElementById('modalTags').innerHTML = '—';
    document.getElementById('modalSessions').innerHTML = '—';
    document.getElementById('modalPhotos').innerHTML = '—';

    // Показать ту же модалку
    excursionModal.show();
};

function collectExcursionFormData() {
    return {
        title: document.getElementById('modalTitle').value,
        description: document.getElementById('modalDescription').value,
        category: document.getElementById('modalCategory').value,
        format_type: document.getElementById('modalFormat').value,
        age_category: document.getElementById('modalAgeCategory').value,
        duration: document.getElementById('modalDuration').value,
        place: document.getElementById('modalPlace').value,
        conducted_by: document.getElementById('modalConductedBy').value,
        working_hours: document.getElementById('modalWorkingHours').value,
        contact_email: document.getElementById('modalContactEmail').value,
        telegram: document.getElementById('modalTelegram').value,
        vk: document.getElementById('modalVk').value,
        is_active: document.getElementById('modalIsActive').value === 'true',
        distance_to_center: document.getElementById('modalDistance').value,
        time_to_nearest_stop: document.getElementById('modalTimeToStop').value,
        iframe_url: document.getElementById('modalIframe').value,

        sessions: originalExcursionData.sessions || [],  // сюда добавляем массив сессий
    };
}
