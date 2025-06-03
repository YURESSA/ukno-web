function renderTable(title, headers, rows) {
    let html = `
    <div class="container mt-4">
      <h2 class="mb-3 text-primary">${title}</h2>`;

    if (rows.length === 0) {
        html += `
      <div class="alert alert-info" role="alert">
        Данные отсутствуют.
      </div>`;
    } else {
        html += `
      <div class="table-responsive">
        <table id="excursionsTable" class="table table-hover table-bordered align-middle border-primary">
          <thead class="table-primary">
            <tr>`;

        for (const h of headers) {
            html += `<th scope="col">${h}</th>`;
        }
        html += `<th scope="col" style="width: 130px;">Действия</th>`;

        html += `</tr>
          </thead>
          <tbody>`;

        for (const row of rows) {
            html += `<tr data-id="${row.id || ''}" style="cursor: pointer;">`;
            for (const cell of row.cells) {
                html += `<td>${cell}</td>`;
            }
            html += `<td>${row.actions}</td>`;
            html += '</tr>';
        }

        html += `
          </tbody>
        </table>
      </div>`;
    }

    html += `</div>`;
    document.getElementById('contentArea').innerHTML = html;
}

function showCreateButton(show, type) {
    const btnUser = document.getElementById('btnCreateUser');
    const btnRef = document.getElementById('btnCreateRef');
    const btnExcurs = document.getElementById('btnCreateExcurs');

    if (type === 'user') {
        btnUser.style.display = show ? 'inline-block' : 'none';
        btnRef.style.display = 'none';
        btnExcurs.style.display = 'none';
    } else if (type === 'ref') {
        btnUser.style.display = 'none';
        btnRef.style.display = show ? 'inline-block' : 'none';
        btnExcurs.style.display = 'none';
    } else if (type === 'excursion') {
        btnUser.style.display = 'none';
        btnRef.style.display = 'none';
        btnExcurs.style.display = show ? 'inline-block' : 'none';
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