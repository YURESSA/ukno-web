function renderTable(title, headers, rows) {
    const pageTitle = document.getElementById('pageTitle');
    if (pageTitle) {
        pageTitle.textContent = title;
    }

    let html = `
    <div class="container mt-4">
      <style>
        /* Минималистичный стиль таблицы */
        #excursionsTable {
          width: 100%;
          border-collapse: collapse;
          font-family: 'Segoe UI', sans-serif;
          font-size: 14px;
        }

        #excursionsTable th,
        #excursionsTable td {
          padding: 10px 12px;
          border: 1px solid #ddd;
          text-align: left;
        }

        #excursionsTable thead {
          background-color: #f8f9fa;
          font-weight: 600;
        }

        #excursionsTable tbody tr:hover {
          background-color: #f1f1f1;
        }

        .container h2 {
          font-size: 20px;
          font-weight: 500;
          margin-bottom: 16px;
          color: #333;
        }

        td:last-child {
          text-align: center;
        }

        .action-btn {
          background: none;
          border: none;
          color: #007bff;
          cursor: pointer;
          padding: 0;
          font-size: 14px;
        }

        .action-btn:hover {
          text-decoration: underline;
        }

        .alert {
          font-family: 'Segoe UI', sans-serif;
          font-size: 14px;
        }
      </style>

      <h2 class="mb-3 text-primary"></h2>`;

    if (rows.length === 0) {
        html += `
      <div class="alert alert-info" role="alert">
        Данные отсутствуют.
      </div>`;
    } else {
        html += `
      <div class="table-responsive">
        <table id="excursionsTable" class="table">
          <thead>
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
    }
    else if (type === 'reservations') {
        btnUser.style.display = 'none';
        btnRef.style.display = 'none';
        btnExcurs.style.display = 'none';
        btnNews.style.display = 'none';
    }
    else {
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