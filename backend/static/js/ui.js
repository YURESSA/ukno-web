function renderTable(title, headers, rows) {
    const pageTitle = document.getElementById('pageTitle');
    if (pageTitle) pageTitle.textContent = title;

    const originalRows = [...rows];

    const renderBody = (dataRows) => {
        return dataRows.map(row => {
            const cellsHtml = row.cells.map(cell => `<td>${cell}</td>`).join('');
            return `<tr data-id="${row.id || ''}" style="cursor:pointer;">${cellsHtml}<td>${row.actions}</td></tr>`;
        }).join('');
    };

    let html = `
    <div class="container mt-4 mb-4">
      <input id="tableFilterInput" type="text" class="form-control mb-2" placeholder="Поиск...">
      <button id="resetSortBtn" class="btn btn-sm btn-outline-secondary mb-3">Сбросить сортировку</button>
      <div class="table-responsive">
        <table id="excursionsTable" class="table table-bordered table-hover" style="border-collapse: collapse;">
          <thead>
            <tr>`;

    headers.forEach((h, i) => {
        html += `
      <th data-index="${i}" class="sortable" style="cursor:pointer; white-space:nowrap;">
        <div style="display:flex; align-items:center; justify-content:space-between; gap:4px;">
          <span>${h}</span>
          <span class="sort-indicator" style="font-size:0.8em;"></span>
        </div>
      </th>`;
    });

    html += `<th style="width:130px;">Действия</th></tr></thead><tbody>`;
    html += renderBody(rows);
    html += `</tbody></table></div></div>`;

    document.getElementById('contentArea').innerHTML = html;

    // Инициализация фильтра, сортировки и кнопки сброса
    initTableFeatures(originalRows, renderBody);
}

function initTableFeatures(originalRows, renderBody) {
    // 🔍 Фильтрация
    const input = document.getElementById('tableFilterInput');
    input.addEventListener('input', () => {
        const filter = input.value.toLowerCase();
        const trs = document.querySelectorAll('#excursionsTable tbody tr');
        trs.forEach(tr => {
            const tds = Array.from(tr.querySelectorAll('td')).map(td => td.textContent.toLowerCase());
            tr.style.display = tds.some(text => text.includes(filter)) ? '' : 'none';
        });
    });

    // 🔃 Мультисортировка
    const sortState = [];

    const thElements = document.querySelectorAll('#excursionsTable th.sortable');
    thElements.forEach(th => {
        th.addEventListener('click', () => {
            const index = +th.dataset.index;
            const existing = sortState.find(s => s.index === index);

            if (existing) {
                existing.asc = !existing.asc;
            } else {
                sortState.unshift({index, asc: true});
            }

            // Сброс иконок
            document.querySelectorAll('.sort-indicator').forEach(el => el.textContent = '');

            // Установка стрелок
            sortState.forEach(({index, asc}) => {
                const th = document.querySelector(`#excursionsTable th[data-index="${index}"]`);
                if (th) {
                    const indicator = th.querySelector('.sort-indicator');
                    if (indicator) indicator.textContent = asc ? '▲' : '▼';
                }
            });

            const tbody = document.querySelector('#excursionsTable tbody');
            const rowsArray = Array.from(tbody.querySelectorAll('tr'));

            rowsArray.sort((a, b) => {
                for (const {index, asc} of sortState) {
                    const aText = a.children[index].innerText;
                    const bText = b.children[index].innerText;
                    const cmp = aText.localeCompare(bText, 'ru', {numeric: true});
                    if (cmp !== 0) return asc ? cmp : -cmp;
                }
                return 0;
            });

            tbody.innerHTML = '';
            rowsArray.forEach(tr => tbody.appendChild(tr));
        });
    });

    // 🔁 Кнопка сброса сортировки
    document.getElementById('resetSortBtn').addEventListener('click', () => {
        sortState.length = 0;

        // Убираем стрелки
        document.querySelectorAll('.sort-indicator').forEach(el => {
            el.textContent = '';
        });

        // Восстановление оригинального порядка
        const tbody = document.querySelector('#excursionsTable tbody');
        tbody.innerHTML = renderBody(originalRows);

        // После замены tbody — заново навесить фильтр (если нужно)
        // Повторно вызываем фильтрацию, чтобы скрытые строки сразу появились корректно
        input.dispatchEvent(new Event('input'));
    });
}



function showCreateButton(show, type) {
    const btnUser = document.getElementById('btnCreateUser');
    const btnRef = document.getElementById('btnCreateRef');
    const btnExcurs = document.getElementById('btnCreateExcurs');
    const btnNews = document.getElementById('btnCreateNews');

    if (type === 'user') {
        btnUser.style.display = show ? 'inline-block' : 'none';
        btnRef.style.display = 'none';
        btnExcurs.style.display = 'none';
        btnNews.style.display = 'none'
    } else if (type === 'ref') {
        btnUser.style.display = 'none';
        btnRef.style.display = show ? 'inline-block' : 'none';
        btnExcurs.style.display = 'none';
        btnNews.style.display = 'none'
    } else if (type === 'excursion') {
        btnUser.style.display = 'none';
        btnRef.style.display = 'none';
        btnExcurs.style.display = show ? 'inline-block' : 'none';
        btnNews.style.display = 'none'
    } else if (type === 'news') {
        btnUser.style.display = 'none';
        btnRef.style.display = 'none';
        btnExcurs.style.display = 'none';
        btnNews.style.display = show ? 'inline-block' : 'none';
    } else if (type === 'reservations') {
        btnUser.style.display = 'none';
        btnRef.style.display = 'none';
        btnExcurs.style.display = 'none';
        btnNews.style.display = 'none';
    } else {
        btnUser.style.display = 'none';
        btnRef.style.display = 'none';
        btnExcurs.style.display = 'none';
    }
}

function setActiveMenu(id) {
    document.querySelectorAll('#sidebar .nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.getElementById(id).classList.add('active');
}