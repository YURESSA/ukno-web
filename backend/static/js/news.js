let currentNewsId = null;

// Загрузка таблицы новостей
async function loadNewsTable() {
    showCreateButton(true, 'news');
    const res = await fetchWithAuth(`${API_BASE}/news`);
    if (!res) return;

    const data = await res.json();
    const rows = data.news.map(news => ({
        id: news.news_id,
        cells: [
            news.news_id,
            news.title,
            news.content.length > 100 ? news.content.substring(0, 100) + '...' : news.content,
            new Date(news.created_at).toLocaleString()
        ],
        actions: `
            <button class="btn btn-outline-danger btn-sm btn-delete-news" data-id="${news.news_id}">
                <i class="fas fa-trash"></i> Удалить
            </button>
        `
    }));

    renderTable('Новости', ['ID', 'Заголовок', 'Содержимое', 'Дата'], rows);

    // Назначение обработчиков клика по строке
    document.querySelectorAll('#excursionsTable tbody tr').forEach(row => {
        row.onclick = async (e) => {
            if (e.target.closest('button')) return;

            const id = row.getAttribute('data-id');
            if (!id) return;

            const res = await fetchWithAuth(`${API_BASE}/news/${id}`);
            if (!res) {
                showNotification('Ошибка загрузки новости', 'danger');
                return;
            }

            const data = await res.json();
            showNewsModal(data);
        };
    });
}

async function showNewsModal(news) {
    currentNewsId = news.news_id;
    document.querySelector('#newsModalTitle').textContent = 'Редактировать новость';
    document.querySelector('#newsTitle').value = news.title;
    document.querySelector('#newsContent').value = news.content;
    document.querySelector('#newsPhotoUpload').value = '';

    const previewContainer = document.querySelector('#newsPhotoPreview');
    previewContainer.innerHTML = '';

    const photos = await loadNewsPhotos(news.news_id);
    photos.forEach(photo => {
        addPhotoToPreview(previewContainer, photo, news.news_id);
    });

    const modal = new bootstrap.Modal(document.getElementById('newsModal'));
    modal.show();
}

async function loadNewsPhotos(newsId) {
    const res = await fetchWithAuth(`${API_BASE}/news/${newsId}/photos`);
    if (res.ok) {
        const data = await res.json();
        return data.photos;
    }
    return [];
}

function addPhotoToPreview(container, photo, newsId) {
    const wrapper = document.createElement('div');
    wrapper.style.position = 'relative';
    wrapper.style.display = 'inline-block';
    wrapper.style.margin = '5px';

    const img = document.createElement('img');
    img.src = `${location.origin}/${photo.image_path}`;
    img.classList.add('news-photo-thumb');
    img.style.width = '150px';
    img.style.height = 'auto';
    img.style.objectFit = 'cover';
    img.style.borderRadius = '4px';
    img.style.display = 'block';

    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = '×';
    deleteBtn.title = 'Удалить фото';
    deleteBtn.style.position = 'absolute';
    deleteBtn.style.top = '5px';
    deleteBtn.style.right = '5px';
    deleteBtn.style.backgroundColor = 'rgba(255,0,0,0.7)';
    deleteBtn.style.border = 'none';
    deleteBtn.style.color = 'white';
    deleteBtn.style.fontWeight = 'bold';
    deleteBtn.style.borderRadius = '50%';
    deleteBtn.style.cursor = 'pointer';


    deleteBtn.dataset.photoId = photo.photo_id;
    deleteBtn.onclick = async () => {
        if (confirm('Удалить фото?')) {
            const res = await fetchWithAuth(`${API_BASE}/news/${newsId}/photos/${deleteBtn.dataset.photoId}`, {
                method: 'DELETE'
            });
            if (res.ok) {
                showNotification('Фото удалено', 'success');
                // Обновляем превью заново
                const updatedPhotos = await loadNewsPhotos(newsId);
                container.innerHTML = '';
                updatedPhotos.forEach(p => addPhotoToPreview(container, p, newsId));
            } else {
                showNotification('Ошибка при удалении фото', 'danger');
            }
        }
    };

    wrapper.appendChild(img);
    wrapper.appendChild(deleteBtn);
    container.appendChild(wrapper);
}


async function loadNewsPhotos(newsId) {
    const res = await fetchWithAuth(`${API_BASE}/news/${newsId}/photos`);
    if (res.ok) {
        const data = await res.json();
        return data.photos;
    }
    return [];
}

// Добавление фотографии
async function addPhotoToNews(newsId, photoFile) {
    const formData = new FormData();
    formData.append('photo', photoFile);

    const res = await fetchWithAuth(`${API_BASE}/news/${newsId}/photos`, {
        method: 'POST',
        body: formData
    });
    if (res.ok) {
        showNotification('Фото добавлено', 'success');
        return await res.json();
    } else {
        showNotification('Ошибка добавления фото', 'danger');
    }
}

// Создание новости
async function createNews(title, content, imageFiles) {
    const formData = new FormData();
    formData.append('data', JSON.stringify({title, content}));
    imageFiles.forEach(file => formData.append('image', file));

    const res = await fetchWithAuth(`${API_BASE}/news`, {
        method: 'POST',
        body: formData
    });

    if (res.ok) {
        showNotification('Новость создана', 'success');
        loadNewsTable();
    } else {
        const err = await res.json();
        showNotification(err.message || 'Ошибка при создании', 'danger');
    }
}

// Удаление новости
document.addEventListener('click', async (e) => {
    if (e.target.closest('.btn-delete-news')) {
        const id = e.target.closest('button').dataset.id;
        if (confirm('Удалить новость?')) {
            const res = await fetchWithAuth(`${API_BASE}/news/${id}`, {
                method: 'DELETE'
            });
            if (res.ok) {
                showNotification('Новость удалена', 'success');
                loadNewsTable();
            } else {
                showNotification('Ошибка при удалении', 'danger');
            }
        }
    }
});

document.getElementById('btnUploadPhoto').addEventListener('click', async () => {
    const input = document.getElementById('newsPhotoUpload');
    const files = input.files;
    if (!files.length) {
        showNotification('Выберите фото для загрузки', 'warning');
        return;
    }

    if (!currentNewsId) {
        showNotification('Сначала выберите или создайте новость', 'warning');
        return;
    }

    const photoFile = files[0];
    try {
        const res = await addPhotoToNews(currentNewsId, photoFile);
        if (res) {
            showNotification('Фото успешно добавлено', 'success');
            const previewContainer = document.querySelector('#newsPhotoPreview');
            // Перезагрузим все фото с сервера
            const photos = await loadNewsPhotos(currentNewsId);
            previewContainer.innerHTML = '';
            photos.forEach(photo => addPhotoToPreview(previewContainer, photo, currentNewsId));
            input.value = ''; // очистить выбор файла
        }
    } catch (e) {
        showNotification('Ошибка при добавлении фото', 'danger');
        console.error(e);
    }
});

document.getElementById('saveNewsBtn').addEventListener('click', async () => {
    const title = document.getElementById('newsTitle').value.trim();
    const content = document.getElementById('newsContent').value.trim();
    const photoInput = document.getElementById('newsPhotoUpload');
    const imageFiles = Array.from(photoInput.files);

    if (!title) {
        showNotification('Введите заголовок новости', 'warning');
        return;
    }
    if (!content) {
        showNotification('Введите содержимое новости', 'warning');
        return;
    }

    try {
        if (currentNewsId === null) {
            // Создание новости
            await createNews(title, content, imageFiles);
        } else {
            // Обновление новости
            await updateNews(currentNewsId, title, content);

            // Если есть фотографии для загрузки — добавляем их
            for (const file of imageFiles) {
                await addPhotoToNews(currentNewsId, file);
            }

            showNotification('Новость обновлена', 'success');
        }

        // Обновляем таблицу и закрываем модалку
        await loadNewsTable();
        const modalEl = document.getElementById('newsModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();

        // Сбрасываем форму и currentNewsId
        currentNewsId = null;
        document.getElementById('newsTitle').value = '';
        document.getElementById('newsContent').value = '';
        photoInput.value = '';
        document.querySelector('#newsPhotoPreview').innerHTML = '';

    } catch (err) {
        console.error(err);
        showNotification('Ошибка при сохранении новости', 'danger');
    }
});

async function updateNews(newsId, title, content) {
    const formData = new FormData();
    formData.append('data', JSON.stringify({ title, content }));

    const res = await fetchWithAuth(`${API_BASE}/news/${newsId}`, {
        method: 'PUT',
        body: formData
    });

    if (!res.ok) {
        const err = await res.json();
        showNotification(err.message || 'Ошибка при обновлении новости', 'danger');
        throw new Error('Ошибка обновления новости');
    }
}
