let currentProjectId = null;
const projectModalEl = document.getElementById('projectModal');
const projectModal = new bootstrap.Modal(projectModalEl);

// Загрузка списка проектов
async function loadProjectSection() {
    showCreateButton(true, 'projects'); // показать кнопку "Добавить проект"
    const res = await fetchWithAuth(`${API_REF_BASE}/projects`);
    if (!res) return;
    const data = await res.json();

    const rows = data.map(project => ({
        id: project.id,
        cells: [
            project.id,
            project.title,
            project.link
        ],
        actions: `
            <button class="btn btn-outline-danger btn-sm btn-delete-project" data-id="${project.id}">
                <i class="fas fa-trash"></i> Удалить
            </button>
        `
    }));

    renderTable('Проекты компании', ['ID', 'Название', 'Ссылка'], rows);

    document.querySelectorAll('#excursionsTable tbody tr').forEach(row => {
        row.onclick = async (e) => {
            if (e.target.closest('button')) return;
            const id = row.dataset.id;
            if (!id) return;
            const res = await fetchWithAuth(`${API_REF_BASE}/projects/${id}`);
            if (!res) {
                showNotification('Ошибка загрузки проекта', 'danger');
                return;
            }
            const data = await res.json();
            showProjectModal(data);
        };
    });

    document.querySelectorAll('.btn-delete-project').forEach(btn => {
        btn.onclick = async (e) => {
            e.stopPropagation();
            const id = btn.dataset.id;
            if (!confirm('Удалить проект?')) return;
            const res = await fetchWithAuth(`${API_REF_BASE}/projects/${id}`, { method: 'DELETE' });
            if (res.ok) {
                showNotification('Проект удалён', 'success');
                loadProjectSection();
            } else {
                showNotification('Ошибка удаления', 'danger');
            }
        };
    });
}

// Показ модалки проекта
function showProjectModal(project) {
    currentProjectId = project?.id || null;
    document.getElementById('projectTitle').value = project?.title || '';
    document.getElementById('projectLink').value = project?.link || '';
    projectModal.show();
}

// Сохранение проекта (создание/обновление)
document.getElementById('projectSaveBtn').addEventListener('click', async () => {
    const title = document.getElementById('projectTitle').value.trim();
    const link = document.getElementById('projectLink').value.trim();

    if (!title || !link) {
        showNotification('Заполните все поля', 'warning');
        return;
    }

    try {
        let res;
        const body = JSON.stringify({ title, link });
        const options = { method: currentProjectId ? 'PUT' : 'POST', headers: { 'Content-Type': 'application/json' }, body };
        const url = currentProjectId ? `${API_REF_BASE}/projects/${currentProjectId}` : `${API_REF_BASE}/projects`;
        res = await fetchWithAuth(url, options);

        if (res.ok) {
            showNotification('Проект сохранён', 'success');
            await loadProjectSection();
            projectModal.hide();
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
projectModalEl.addEventListener('hidden.bs.modal', () => {
    currentProjectId = null;
    document.getElementById('projectTitle').value = '';
    document.getElementById('projectLink').value = '';
});

// Создание нового проекта
document.getElementById('btnCreateProject').addEventListener('click', () => showProjectModal(null));
