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
    const res = await fetchWithAuth(`${API_BASE}/reservations`);
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
            `<button class="btn btn-outline-danger btn-sm btn-delete-ref" data-ref="reservation" data-id="${r.reservation_id}">
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


    document.querySelectorAll('#excursionsTable tbody tr').forEach(row => {
        row.onclick = async (e) => {
            if (e.target.closest('button')) return;

            const id = row.getAttribute('data-id');
            if (!id) return;

            const res = await fetchWithAuth(`${API_BASE}/reservations/${id}`);
            if (!res) {
                showNotification('Ошибка загрузки бронирования', 'danger');
                return;
            }

            const data = await res.json();
            showReservationModal(data);
        };
    });

    // Обработчики кнопок удаления в таблице
    document.querySelectorAll('.btn-delete-ref').forEach(btn => {
        btn.onclick = async (e) => {
            e.stopPropagation();
            const id = btn.getAttribute('data-id');
            if (!id) return;

            await deleteReservationById(id, loadReservations);
        };
    });
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
