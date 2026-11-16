/* QR decoding is local: only the decoded ticket is sent to the authenticated API. */
const ticketStatusLabels = {
    valid: 'Вход разрешён', partially_used: 'Часть группы уже вошла', fully_used: 'Все участники уже вошли',
    cancelled: 'Бронь отменена', unpaid: 'Бронь не оплачена', unavailable: 'Событие недоступно',
    wrong_session: 'Билет на другой сеанс'
};

async function ticketRequest(path, options = {}) {
    const response = await fetch(path, {
        ...options, headers: {
            Authorization: `Bearer ${TOKEN}`, ...(options.body ? {'Content-Type': 'application/json'} : {})
        }
    });
    if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        const error = new Error(data.message || 'Не удалось выполнить запрос');
        error.status = response.status;
        throw error;
    }
    return response;
}

function openTicketScanner() {
    document.getElementById('reservationTicketDialog')?.close();
    const dialog = document.createElement('dialog');
    dialog.id = 'reservationTicketDialog';
    dialog.className = 'ticket-dialog';
    dialog.setAttribute('aria-labelledby', 'ticket-dialog-title');
    dialog.innerHTML = `
      <div class="reservation-section-heading ticket-dialog-header" style="margin:0;padding:22px 24px;border-bottom:1px solid #e2e8f0;">
        <div><h2 id="ticket-dialog-title">Проверка QR-билета</h2><p>Проверьте бронь и отметьте, сколько гостей входит.</p></div>
        <button class="ticket-dialog-close" type="button" aria-label="Закрыть">×</button>
      </div>
      <div class="ticket-dialog-body">
        <form data-ticket-check>
          <div class="ticket-actions">
            <button type="button" class="btn btn-outline-primary" data-camera>Открыть камеру</button>
            <button type="button" class="btn btn-outline-secondary" data-photo>Загрузить фото QR</button>
            <input type="file" accept="image/*" data-file hidden aria-label="Изображение QR-билета">
          </div>
          <video class="ticket-camera" autoplay muted playsinline hidden></video>
          <label for="ticket-code">Код билета</label>
          <textarea id="ticket-code" name="ticket" rows="2" required placeholder="Отсканируйте QR или вставьте код билета" autocomplete="off" spellcheck="false" maxlength="256"></textarea>
          <button class="btn btn-primary" data-check type="submit">Проверить билет</button>
        </form>
        <p class="ticket-message" role="status" aria-live="polite" hidden></p>
        <div data-ticket-result></div>
      </div>`;
    const state = {closed: false, busy: false, pending: null, stream: null, timer: null, qrUrl: null,
        ticket: null, ticketCode: '', controller: new AbortController()};
    dialog.ticketState = state;
    const form = dialog.querySelector('form');
    const codeField = form.elements.ticket;
    const video = dialog.querySelector('video');
    const result = dialog.querySelector('[data-ticket-result]');
    const notice = dialog.querySelector('[role="status"]');
    function message(text, tone = '') {
        if (state.closed) return;
        notice.hidden = false; notice.textContent = text; notice.dataset.tone = tone;
    }
    function busy(value) {
        state.busy = value;
        dialog.querySelectorAll('button:not(.ticket-dialog-close)').forEach(button => { button.disabled = value; });
        const locked = value || !!state.pending;
        codeField.disabled = locked;
        const count = dialog.querySelector('[data-entry-count]');
        if (count) count.disabled = locked;
        if (state.pending) dialog.querySelectorAll('[data-camera],[data-photo],[data-check],[data-another]').forEach(button => { button.disabled = true; });
    }
    function stopCamera() {
        clearTimeout(state.timer);
        if (state.stream) state.stream.getTracks().forEach(track => track.stop());
        state.stream = null; video.srcObject = null; video.hidden = true;
        dialog.querySelector('[data-camera]').textContent = 'Открыть камеру';
    }
    function cleanup() {
        state.closed = true;
        state.controller.abort();
        stopCamera();
        if (state.qrUrl) URL.revokeObjectURL(state.qrUrl);
        dialog.remove();
    }
    dialog.addEventListener('close', cleanup, {once: true});
    dialog.querySelector('.ticket-dialog-close').onclick = () => dialog.close();
    dialog.addEventListener('click', event => {
        if (event.target === dialog) {
            const box = dialog.getBoundingClientRect();
            if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
        }
    });

    function renderTicket(ticket) {
        if (state.closed) return;
        state.ticket = ticket;
        result.innerHTML = `
          <section class="ticket-result" aria-label="Результат проверки">
            <div class="ticket-result-heading"><h3 data-name></h3><p data-event></p><p data-date></p><span class="ticket-status"></span></div>
            <div class="ticket-counts"><div><strong data-total></strong><span>в брони</span></div><div><strong data-entered></strong><span>уже вошли</span></div><div><strong data-remaining></strong><span>могут войти</span></div></div>
            <div class="ticket-entry" data-entry><div><label for="ticket-count">Входят сейчас</label><input id="ticket-count" data-entry-count type="number" min="1" step="1" value="1" required></div><button type="button" class="btn btn-primary" data-admit>Отметить вход</button></div>
          </section><button type="button" class="btn btn-outline-secondary" style="margin-top:16px;" data-another>Проверить другой билет</button>`;
        result.querySelector('[data-name]').textContent = ticket.full_name || 'Участник';
        result.querySelector('[data-event]').textContent = ticket.event_title || 'Событие';
        result.querySelector('[data-date]').textContent = `Бронь #${ticket.reservation_id} · сеанс #${ticket.session_id} · ${new Date(ticket.session_start_datetime).toLocaleString('ru-RU')}`;
        const status = result.querySelector('.ticket-status');
        status.textContent = ticketStatusLabels[ticket.status] || 'Вход недоступен';
        status.dataset.invalid = String(!ticket.can_enter);
        result.querySelector('[data-total]').textContent = ticket.participants_count;
        result.querySelector('[data-entered]').textContent = ticket.checked_in_count;
        result.querySelector('[data-remaining]').textContent = ticket.remaining_count;
        result.querySelector('[data-entry]').hidden = !ticket.can_enter;
        result.querySelector('[data-entry-count]').max = ticket.remaining_count;
        result.querySelector('[data-admit]').onclick = admit;
        result.querySelector('[data-another]').onclick = () => {
            if (state.pending || state.busy) return;
            if (state.qrUrl) URL.revokeObjectURL(state.qrUrl);
            state.qrUrl = null; state.ticket = null; state.ticketCode = '';
            codeField.value = ''; form.hidden = false; notice.hidden = true;
            result.replaceChildren(); codeField.focus();
        };
        if (state.qrUrl) appendQR();
    }

    function appendQR() {
        const qr = document.createElement('div'); qr.className = 'ticket-qr';
        const image = document.createElement('img'); image.src = state.qrUrl; image.alt = 'QR-билет на бронирование';
        const caption = document.createElement('p'); caption.textContent = 'Один билет на всех участников этой брони.';
        qr.append(image, caption); result.querySelector('section').append(qr);
    }

    async function check() {
        if (state.busy || state.pending || !form.reportValidity()) return;
        stopCamera(); busy(true);
        result.replaceChildren();
        try {
            const code = codeField.value.trim();
            const response = await ticketRequest(`${API_BASE}/reservations/tickets/check`, {
                method: 'POST', signal: state.controller.signal,
                body: JSON.stringify({ticket: code})
            });
            const data = await response.json();
            state.ticketCode = code;
            form.hidden = data.ticket.can_enter;
            renderTicket(data.ticket);
            message(data.ticket.can_enter ? 'Билет проверен. Укажите количество входящих гостей.' : ticketStatusLabels[data.ticket.status], data.ticket.can_enter ? 'success' : 'error');
        } catch (error) {
            if (!state.closed) message(error.message, 'error');
        } finally { if (!state.closed) busy(false); }
    }

    async function admit() {
        if (state.busy || !state.ticket?.can_enter) return;
        const countField = result.querySelector('[data-entry-count]');
        if (!state.pending && !countField.reportValidity()) return;
        if (!state.pending) state.pending = {
            ticket: state.ticketCode, session_id: state.ticket.session_id,
            count: Number(countField.value), request_id: crypto.randomUUID()
        };
        busy(true);
        try {
            const response = await ticketRequest(`${API_BASE}/reservations/tickets/check-in`, {
                method: 'POST', body: JSON.stringify(state.pending), signal: state.controller.signal
            });
            const data = await response.json();
            state.pending = null;
            renderTicket(data.ticket);
            message(data.replayed ? 'Этот вход уже зарегистрирован. Повторного списания нет.' : `Вход отмечен: ${data.admission.participants_count}. Осталось мест: ${data.ticket.remaining_count}.`, 'success');
        } catch (error) {
            if (state.closed) return;
            if (error.status && error.status < 500) {
                state.pending = null;
                message(`${error.message}. Проверьте билет ещё раз.`, 'error');
                form.hidden = false;
                result.replaceChildren(); state.ticket = null;
            } else {
                message('Не удалось получить подтверждение. Повторите запрос этой кнопкой — участники не будут списаны дважды.', 'error');
                result.querySelector('[data-admit]').textContent = 'Повторить отметку входа';
            }
        } finally { if (!state.closed) busy(false); }
    }

    form.onsubmit = event => { event.preventDefault(); return check(); };
    form.addEventListener('input', () => {
        if (!state.pending && !state.busy) { state.ticket = null; result.replaceChildren(); notice.hidden = true; }
    });
    const canvas = document.createElement('canvas');
    function decode(image, width, height) {
        const scale = Math.min(1, 1400 / Math.max(width, height));
        canvas.width = Math.round(width * scale); canvas.height = Math.round(height * scale);
        const context = canvas.getContext('2d', {willReadFrequently: true});
        context.drawImage(image, 0, 0, canvas.width, canvas.height);
        const frame = context.getImageData(0, 0, canvas.width, canvas.height);
        return jsQR(frame.data, frame.width, frame.height)?.data;
    }
    dialog.querySelector('[data-camera]').onclick = async () => {
        if (state.stream) { stopCamera(); return; }
        if (state.busy || state.pending || state.cameraOpening) return;
        state.cameraOpening = true;
        const cameraButton = dialog.querySelector('[data-camera]');
        cameraButton.disabled = true;
        try {
            if (!navigator.mediaDevices?.getUserMedia) throw new Error('Камера недоступна. Откройте сайт по HTTPS или загрузите фото QR.');
            const stream = await navigator.mediaDevices.getUserMedia({audio: false, video: {facingMode: {ideal: 'environment'}, width: {ideal: 1280}}});
            if (state.closed || form.hidden || state.busy || state.pending) { stream.getTracks().forEach(track => track.stop()); return; }
            state.stream = stream; video.srcObject = stream; video.hidden = false;
            await video.play();
            dialog.querySelector('[data-camera]').textContent = 'Остановить камеру';
            message('Наведите камеру на QR-билет. Событие и сеанс определятся автоматически.');
            const scan = () => {
                if (state.closed || !state.stream) return;
                try {
                    const code = video.readyState >= 2 && decode(video, video.videoWidth, video.videoHeight);
                    if (code) { codeField.value = code; stopCamera(); check(); return; }
                    state.timer = setTimeout(scan, 200);
                } catch (error) { stopCamera(); message('Не удалось прочитать камеру. Попробуйте загрузить фото QR.', 'error'); }
            };
            scan();
        } catch (error) { stopCamera(); message(error.name === 'NotAllowedError' ? 'Доступ к камере запрещён. Разрешите его в браузере или загрузите фото QR.' : error.message, 'error'); }
        finally { state.cameraOpening = false; if (!state.closed) cameraButton.disabled = state.busy || !!state.pending; }
    };
    const fileInput = dialog.querySelector('[data-file]');
    dialog.querySelector('[data-photo]').onclick = () => fileInput.click();
    fileInput.onchange = async () => {
        const file = fileInput.files[0];
        if (!file || state.busy || state.pending) return;
        if (file.size > 15 * 1024 * 1024) { message('Изображение должно быть не больше 15 МБ.', 'error'); return; }
        stopCamera();
        const url = URL.createObjectURL(file);
        try {
            const image = new Image();
            await new Promise((resolve, reject) => { image.onload = resolve; image.onerror = () => reject(new Error('Не удалось открыть изображение')); image.src = url; });
            if (state.closed) return;
            const code = decode(image, image.naturalWidth, image.naturalHeight);
            if (!code) throw new Error('QR-код не найден. Загрузите более чёткое изображение.');
            codeField.value = code;
            await check();
        } catch (error) { message(error.message, 'error'); }
        finally { URL.revokeObjectURL(url); fileInput.value = ''; }
    };

    dialog.showTicket = async ticket => {
        stopCamera();
        state.ticketCode = ticket.qr_payload;
        form.hidden = true;
        dialog.querySelector('h2').textContent = 'QR-билет на бронь';
        renderTicket(ticket);
        const response = await ticketRequest(ticket.qr_svg_url, {signal: state.controller.signal});
        const url = URL.createObjectURL(await response.blob());
        if (state.closed) { URL.revokeObjectURL(url); return; }
        state.qrUrl = url;
        appendQR();
    };
    dialog.showError = message;
    document.body.append(dialog);
    dialog.showModal();
    return dialog;
}

async function openReservationTicket(reservationId) {
    const dialog = openTicketScanner();
    try {
        const response = await ticketRequest(`${API_BASE}/reservations/${reservationId}/ticket`, {signal: dialog.ticketState.controller.signal});
        const data = await response.json();
        if (!dialog.ticketState.closed) await dialog.showTicket(data.ticket);
    } catch (error) { if (!dialog.ticketState.closed) dialog.showError(error.message, 'error'); }
}
