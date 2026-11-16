// Run from the repository root: node tests/test_reservation_filters.cjs
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { JSDOM } = require('../frontend/node_modules/jsdom');

async function main() {
    const dom = new JSDOM('<div id="contentArea"></div>', { runScripts: 'outside-only' });
    const window = dom.window;
    const calls = [];
    let downloads = 0;
    let revoked = false;
    window.API_BASE = '/api/admin';
    window.showCreateButton = () => {};
    window.showNotification = message => { throw new Error(message); };
    window.renderTable = () => {
        window.document.getElementById('contentArea').innerHTML =
            '<input id="tableFilterInput"><table id="excursionsTable"><tbody></tbody></table>';
    };
    window.fetchWithAuth = async url => {
        calls.push(url);
        return {
            ok: true,
            json: async () => url.endsWith('/excursions')
                ? { excursions: [{ excursion_id: 12, title: 'Событие' }] }
                : { reservations: [] },
            blob: async () => new window.Blob(['xlsx'])
        };
    };
    window.URL.createObjectURL = () => 'blob:test';
    window.URL.revokeObjectURL = () => { revoked = true; };
    window.setTimeout = callback => callback();
    window.HTMLAnchorElement.prototype.click = function () {
        assert.equal(this.download, 'reservations.xlsx');
        assert.equal(this.href, 'blob:test');
        downloads++;
    };
    window.eval(fs.readFileSync('backend/static/js/reservations.js', 'utf8'));
    await window.loadReservations();
    let form = window.document.querySelector('form');
    form.elements.event_id.value = '12';
    form.elements.date_from.value = '2026-11-01';
    form.elements.date_to.value = '2026-11-30';
    form.elements.is_paid.value = 'true';
    form.elements.q.value = 'Иван +7';
    await form.onsubmit({ preventDefault() {} });
    const listParams = new URL(calls.at(-1), 'https://example.com').searchParams;
    assert.equal(listParams.get('event_id'), '12');
    assert.equal(listParams.get('q'), 'Иван +7');
    assert.equal(listParams.get('is_paid'), 'true');
    assert.equal(listParams.get('date_to'), '2026-11-30');
    assert.equal(listParams.has('is_cancelled'), false);
    form = window.document.querySelector('form');
    assert.equal(form.elements.event_id.value, '12');
    assert.equal(form.elements.q.value, 'Иван +7');
    const button = form.querySelector('[data-export]');
    await button.onclick({ currentTarget: button });
    const exportParams = new URL(calls.at(-1), 'https://example.com').searchParams;
    assert.equal(exportParams.get('format'), 'xlsx');
    exportParams.delete('format');
    assert.equal(exportParams.toString(), listParams.toString());
    assert.equal(button.disabled, false);
    assert.equal(downloads, 1);
    assert.ok(revoked);
    await form.querySelector('[data-reset]').onclick();
    assert.equal(new URL(calls.at(-1), 'https://example.com').search, '');
    assert.equal(window.document.querySelector('form').elements.q.value, '');
    dom.window.close();
    console.log('PASS: filters, state restoration, matching Excel request, download and reset');
}

main().catch(error => { console.error(error); process.exitCode = 1; });
