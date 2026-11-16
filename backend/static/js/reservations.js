let reservationFilters = new URLSearchParams();
let reservationEvents = null;

function renderReservationFilters() {
    const form = document.createElement('form');
    form.className = 'reservation-filters';
    form.innerHTML = `
      <div class="reservation-section-heading">
        <div><h2>Фильтры бронирований</h2><p>Найдите нужные брони или выгрузите выбранные записи в Excel.</p></div>
        <button type="button" class="btn btn-outline-primary" data-scan><i class="fas fa-qrcode me-2" aria-hidden="true"></i>Проверить QR-билет</button>
      </div>
      <div class="reservation-filter-grid">
        <div class="reservation-field wide"><label for="reservation-event">Событие</label>
          <select id="reservation-event" name="event_id"><option value="">Все события</option></select></div>
        <div class="reservation-field wide"><label for="reservation-search">Поиск по участнику</label>
          <input id="reservation-search" name="q" placeholder="ФИО, телефон или email" maxlength="255"></div>
        <div class="reservation-field narrow"><label for="reservation-session">ID сеанса</label>
          <input id="reservation-session" name="session_id" type="number" min="1" step="1" placeholder="Любой"></div>
        <div class="reservation-field narrow"><label for="reservation-user">ID пользователя</label>
          <input id="reservation-user" name="user_id" type="number" min="1" step="1" placeholder="Любой"></div>
        ${[['date_from', 'Дата события · с'], ['date_to', 'Дата события · по'],
            ['booked_from', 'Дата бронирования · с'], ['booked_to', 'Дата бронирования · по']].map(([name, label]) =>
            `<div class="reservation-field"><label for="reservation-${name}">${label}</label>
              <input id="reservation-${name}" name="${name}" type="date"></div>`).join('')}
        ${[['is_paid', 'Оплата'], ['is_cancelled', 'Отмена']].map(([name, label]) =>
            `<div class="reservation-field"><label for="reservation-${name}">${label}</label>
              <select id="reservation-${name}" name="${name}"><option value="">Любой статус</option>
                <option value="true">${name === 'is_paid' ? 'Оплачена' : 'Отменена'}</option>
                <option value="false">${name === 'is_paid' ? 'Не оплачена' : 'Не отменена'}</option></select></div>`).join('')}
        <div class="reservation-field"><label for="reservation-payment">Статус платежа</label>
          <select id="reservation-payment" name="payment_status"><option value="">Все платежи</option>
            <option value="unpaid">Без платежа</option><option value="pending">Ожидает оплаты</option>
            <option value="waiting_for_capture">Ожидает подтверждения</option>
            <option value="succeeded">Оплачен</option><option value="canceled">Отменён</option></select></div>
      </div>
      <div class="reservation-filter-actions">
        <button class="btn btn-primary" type="submit">Применить фильтры</button>
        <button class="btn btn-outline-secondary" type="button" data-reset>Сбросить</button>
        <button class="btn btn-success" type="button" data-export><i class="fas fa-file-excel me-2" aria-hidden="true"></i>Выгрузить в Excel</button>
      </div>`;
    form.querySelector('[data-scan]').onclick = () => openTicketScanner();
    const grid = form.querySelector('.reservation-filter-grid');
    const advanced = document.createElement('details');
    advanced.className = 'reservation-advanced';
    advanced.dataset.mobileDetails = 'true';
    const extraFilters = [...reservationFilters.keys()].filter(key => !['event_id', 'q'].includes(key)).length;
    advanced.dataset.active = String(extraFilters > 0);
    advanced.open = window.innerWidth > 768 || extraFilters > 0;
    const summary = document.createElement('summary');
    summary.textContent = `Дополнительные фильтры${extraFilters ? ` · ${extraFilters}` : ''}`;
    const advancedGrid = document.createElement('div');
    advancedGrid.className = 'reservation-advanced-grid';
    [...grid.children].slice(2).forEach(field => advancedGrid.append(field));
    advanced.dataset.active = String([...reservationFilters.keys()].some(key => !['event_id', 'q'].includes(key)));
    advanced.open = window.innerWidth > 768 || advanced.dataset.active === 'true';
    advanced.append(summary, advancedGrid); grid.append(advanced);
    for (const event of reservationEvents || []) {
        form.elements.event_id.add(new Option(event.title, event.excursion_id));
    }
    for (const [name, value] of reservationFilters) {
        if (form.elements[name]) form.elements[name].value = value;
    }
    const readFilters = () => new URLSearchParams(
        [...new FormData(form)].filter(([, value]) => value !== '')
    );
    form.onsubmit = async event => {
        event.preventDefault();
        reservationFilters = readFilters();
        await loadReservations();
    };
    form.querySelector('[data-reset]').onclick = async () => {
        reservationFilters = new URLSearchParams();
        await loadReservations();
    };
    form.querySelector('[data-export]').onclick = async event => {
        if (!form.reportValidity()) return;
        const button = event.currentTarget;
        button.disabled = true;
        try {
            const params = readFilters();
            params.set('format', 'xlsx');
            const response = await fetchWithAuth(`${API_BASE}/reservations?${params}`);
            if (!response || !response.ok) return;
            const url = URL.createObjectURL(await response.blob());
            const link = document.createElement('a');
            link.href = url;
            link.download = 'reservations.xlsx';
            document.body.appendChild(link);
            link.click();
            link.remove();
            setTimeout(() => URL.revokeObjectURL(url), 1000);
        } catch (error) {
            showNotification('Не удалось скачать Excel. Повторите попытку', 'danger');
        } finally {
            button.disabled = false;
        }
    };
    const content = document.getElementById('contentArea');
    const table = content.querySelector('.container');
    if (table) {
        table.classList.add('reservations-table');
        const heading = document.createElement('div');
        heading.className = 'reservation-table-heading';
        const count = document.createElement('span');
        count.textContent = `Найдено бронирований: ${document.querySelectorAll('#excursionsTable tbody tr').length}`;
        heading.append(count);
        const resetSort = document.getElementById('resetSortBtn');
        if (resetSort) heading.append(resetSort);
        table.prepend(heading);
    }
    content.prepend(form);
    // Search is server-side so the same selection can be exported.
    document.getElementById('tableFilterInput').style.display = 'none';
}

async function deleteReservationById(id, onSuccess) {
    if (!confirm(`Вы действительно хотите удалить бронирование #${id}?`)) {
        return;
    }
    const res = await fetchWithAuth(`${API_BASE}/reservations/${id}`, {
        method: 'DELETE'
    });
    if (!res || !res.ok) {
        showNotification('Ошибка удаления бронирования', 'danger');
        return;
    }
    showNotification('Бронирование успешно удалено', 'success');
    if (onSuccess) await onSuccess();
}

async function loadReservations() {
    showCreateButton(false); // нет кнопки "создать"
    if (reservationEvents === null) {
        const eventsResponse = await fetchWithAuth(`${API_BASE}/excursions`);
        if (eventsResponse && eventsResponse.ok) {
            reservationEvents = (await eventsResponse.json()).excursions || [];
        }
    }
    const res = await fetchWithAuth(`${API_BASE}/reservations?${reservationFilters}`);
    if (!res || !res.ok) {
        showNotification('Ошибка загрузки бронирований', 'danger');
        return;
    }

    const data = await res.json();
    const reservations = data.reservations || [];

    const rows = reservations.map(r => ({
        id: r.reservation_id,
        cells: [
            r.reservation_id,
            r.session_id,
            r.user_id,
            r.full_name || '—',
            r.phone_number || '—',
            r.email || '—',
            r.participants_count,
            r.is_cancelled ? 'Да' : 'Нет',
            new Date(r.booked_at).toLocaleString(),
            r.is_paid ? 'Да' : 'Нет',                  // добавлено: оплачена
            r.payment_status || '—',                   // статус оплаты
            r.total_cost != null ? r.total_cost + ' ₽' : '—'  // сумма оплаты
        ],
        actions:
            `<button class="btn btn-outline-primary btn-sm reservation-ticket-button" data-ticket-id="${r.reservation_id}">QR-билет</button><button class="btn btn-outline-danger btn-sm btn-delete-ref" data-ref="reservation" data-id="${r.reservation_id}">
        <i class="fas fa-trash me-1"></i> Удалить
     </button>`
    }));


    renderTable('Бронирования', [
        'ID',
        'Сессия',
        'Пользователь',
        'ФИО',
        'Телефон',
        'Email',
        'Участников',
        'Отменена',
        'Дата брони',
        'Оплачена',
        'Статус оплаты',
        'Сумма оплаты'
    ], rows);
    renderReservationFilters();


    // Delegate actions so resetting table sorting does not discard their handlers.
    document.getElementById('excursionsTable').onclick = async event => {
        const ticketButton = event.target.closest('[data-ticket-id]');
        if (ticketButton) {
            await openReservationTicket(Number(ticketButton.dataset.ticketId));
            return;
        }
        const deleteButton = event.target.closest('.btn-delete-ref');
        if (deleteButton) {
            await deleteReservationById(deleteButton.dataset.id, loadReservations);
            return;
        }
        const row = event.target.closest('tbody tr');
        if (!row || event.target.closest('button')) return;
        const id = row.dataset.id;
        if (!id) return;
        const response = await fetchWithAuth(`${API_BASE}/reservations/${id}`);
        if (!response) return;
        showReservationModal(await response.json());
    };
}


function showReservationModal(data) {
    const reservation = data.reservation;
    const detailsDiv = document.getElementById('reservationDetails');

    if (!reservation) {
        detailsDiv.innerHTML = '<p class="fs-6">Нет данных для отображения.</p>';
        return;
    }

    const formatBool = (val) =>
        val ? '<span class="badge bg-success">Да</span>' : '<span class="badge bg-danger">Нет</span>';

    const formatCurrency = (val) =>
        val != null ? `${val.toLocaleString()} ₽` : '—';

    const formatDate = (val) =>
        val ? new Date(val).toLocaleString() : '—';

    detailsDiv.innerHTML = `
    <div class="border-bottom pb-3 mb-4">
      <h5 class="fw-bold fs-5 d-flex align-items-center gap-2 mb-0">
        <i class="fas fa-user-check text-primary"></i>
        Бронирование #${reservation.reservation_id}
      </h5>
    </div>

    <dl class="row fs-6">
      <dt class="col-sm-4">ФИО:</dt>
      <dd class="col-sm-8">${reservation.full_name || '—'}</dd>

      <dt class="col-sm-4">Телефон:</dt>
      <dd class="col-sm-8">${reservation.phone_number || '—'}</dd>

      <dt class="col-sm-4">Email:</dt>
      <dd class="col-sm-8">${reservation.email || '—'}</dd>

      <dt class="col-sm-4">Количество участников:</dt>
      <dd class="col-sm-8">${reservation.participants_count}</dd>

      <dt class="col-sm-4">Оплачена:</dt>
      <dd class="col-sm-8">${formatBool(reservation.is_paid)}</dd>

      <dt class="col-sm-4">Статус оплаты:</dt>
      <dd class="col-sm-8">${reservation.payment_status || '—'}</dd>

      <dt class="col-sm-4">Сумма оплаты:</dt>
      <dd class="col-sm-8">${formatCurrency(reservation.total_cost)}</dd>

      <dt class="col-sm-4">Отменена:</dt>
      <dd class="col-sm-8">${formatBool(reservation.is_cancelled)}</dd>

      <dt class="col-sm-4">Дата бронирования:</dt>
      <dd class="col-sm-8">${formatDate(reservation.booked_at)}</dd>

      <dt class="col-sm-4">Экскурсия:</dt>
      <dd class="col-sm-8">${reservation.excursion_title || '—'}</dd>

      <dt class="col-sm-4">Время сессии:</dt>
      <dd class="col-sm-8">${formatDate(reservation.session_start_datetime)}</dd>
    </dl>

    <div class="text-end mt-4">
      <button id="deleteReservationBtn" class="btn btn-outline-danger btn-lg">
        <i class="fas fa-trash-alt me-1"></i> Удалить бронирование
      </button>
    </div>
  `;

    const reservationModalEl = document.getElementById('reservationModal');
    const reservationModal = new bootstrap.Modal(reservationModalEl);
    reservationModal.show();

    const deleteBtn = document.getElementById('deleteReservationBtn');
    if (deleteBtn) {
        deleteBtn.onclick = async () => {
            await deleteReservationById(reservation.reservation_id, async () => {
                reservationModal.hide();
                await loadReservations();
            });
        };
    }
}
