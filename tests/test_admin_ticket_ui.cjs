// Run: node tests/test_admin_ticket_ui.cjs
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { randomUUID } = require('node:crypto');
const { JSDOM } = require('../frontend/node_modules/jsdom');

async function main() {
    const dom = new JSDOM('<body></body>', {url: 'https://example.test', runScripts: 'outside-only'});
    const w = dom.window;
    w.API_BASE = '/api/admin'; w.TOKEN = 'test-admin-token';
    w.reservationEvents = [{title: 'Прогулка', sessions: [{session_id: 7, start_datetime: '2026-11-28T18:30:00'}]}];
    Object.defineProperty(w.crypto, 'randomUUID', {value: randomUUID});
    w.HTMLDialogElement.prototype.showModal = function () { this.open = true; };
    w.HTMLDialogElement.prototype.close = function () { this.open = false; this.dispatchEvent(new w.Event('close')); };
    w.URL.createObjectURL = () => 'blob:qr';
    let revoked = 0;
    w.URL.revokeObjectURL = () => revoked++;
    const ticketCode = 'ukno:ticket:v1:' + 'A'.repeat(43);
    let entered = 0;
    const ticket = () => ({reservation_id: 42, session_id: 7, event_title: 'Прогулка',
        full_name: '<img src=x onerror=bad>', session_start_datetime: '2026-11-28T18:30:00',
        participants_count: 3, checked_in_count: entered, remaining_count: 3 - entered,
        status: entered === 3 ? 'fully_used' : entered ? 'partially_used' : 'valid', can_enter: entered < 3});
    const requests = [];
    let failNextEntry = true;
    w.fetch = async (url, options) => {
        assert.equal(options.headers.Authorization, 'Bearer test-admin-token');
        const body = options.body ? JSON.parse(options.body) : null;
        requests.push({url, body});
        if (url.endsWith('/check-in')) {
            if (failNextEntry) { failNextEntry = false; throw new Error('Connection lost'); }
            entered += body.count;
            return {ok: true, json: async () => ({ticket: ticket(), admission: {participants_count: body.count}, replayed: false})};
        }
        if (url.endsWith('/qr')) return {ok: true, blob: async () => new w.Blob(['svg'])};
        return {ok: true, json: async () => ({ticket: {...ticket(), qr_payload: ticketCode,
            qr_svg_url: '/api/admin/reservations/42/ticket/qr'}})};
    };
    w.eval(fs.readFileSync('backend/static/js/reservation_tickets.js', 'utf8'));
    const dialog = w.openTicketScanner();
    const form = dialog.querySelector('form');
    assert.equal(form.elements.session_id, undefined); form.elements.ticket.value = ticketCode;
    await form.onsubmit({preventDefault() {}});
    assert.equal(dialog.querySelector('[data-remaining]').textContent, '3');
    assert.deepEqual(requests.find(r => r.url.endsWith('/check')).body, {ticket: ticketCode});
    assert.equal(dialog.querySelector('[data-name]').textContent, '<img src=x onerror=bad>');
    assert.equal(dialog.querySelector('[data-name] img'), null);
    const count = dialog.querySelector('[data-entry-count]');
    count.value = '2';
    let button = dialog.querySelector('[data-admit]');
    await button.onclick();
    assert.ok(dialog.ticketState.pending);
    assert.equal(count.disabled, true);
    assert.equal(button.disabled, false);
    assert.equal(dialog.querySelector('[data-check]').disabled, true);
    await button.onclick();
    const entries = requests.filter(r => r.url.endsWith('/check-in'));
    assert.equal(entries.length, 2);
    assert.deepEqual(entries[0].body, entries[1].body);
    assert.equal(entered, 2);
    assert.equal(dialog.querySelector('[data-remaining]').textContent, '1');
    assert.equal(dialog.ticketState.pending, null);
    dialog.querySelector('[data-entry-count]').value = '1';
    await dialog.querySelector('[data-admit]').onclick();
    assert.equal(dialog.querySelector('[data-remaining]').textContent, '0');
    assert.equal(dialog.querySelector('[data-entry]').hidden, true);
    dialog.close();
    assert.equal(w.document.getElementById('reservationTicketDialog'), null);
    entered = 0;
    await w.openReservationTicket(42);
    const booking = w.document.getElementById('reservationTicketDialog');
    assert.equal(booking.querySelector('form').hidden, true);
    assert.equal(booking.querySelector('.ticket-qr img').src, 'blob:qr');
    booking.close();
    assert.equal(revoked, 1);
    // Camera permission may resolve after closing: its tracks must still be stopped.
    let resolveCamera, stops = 0;
    Object.defineProperty(w.navigator, 'mediaDevices', {value: {
        getUserMedia: () => new Promise(resolve => { resolveCamera = resolve; })
    }});
    const cameraDialog = w.openTicketScanner();
    const cameraPromise = cameraDialog.querySelector('[data-camera]').onclick();
    cameraDialog.close();
    resolveCamera({getTracks: () => [{stop: () => stops++}]});
    await cameraPromise;
    assert.equal(stops, 1);
    console.log('PASS: QR check, partial entry, retry UUID, safe rendering, ticket display and camera cleanup');
}
main().catch(error => {console.error(error); process.exitCode = 1;});
