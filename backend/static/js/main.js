document.addEventListener('DOMContentLoaded', () => {
    window.sessionModal = new bootstrap.Modal(document.getElementById('sessionModal'));

    // Обработчики меню
    document.getElementById('btnUsers').onclick = e => {
        e.preventDefault();
        setActiveMenu('btnUsers');
        localStorage.setItem('admin_current_section', 'users');
        loadUsers();
    };

    document.getElementById('btnRoles').onclick = e => {
        e.preventDefault();
        setActiveMenu('btnRoles');
        localStorage.setItem('admin_current_section', 'roles');
        loadReference('roles');
    };

    document.getElementById('btnCategories').onclick = e => {
        e.preventDefault();
        setActiveMenu('btnCategories');
        localStorage.setItem('admin_current_section', 'categories');
        loadReference('categories');
    };

    document.getElementById('btnFormatTypes').onclick = e => {
        e.preventDefault();
        setActiveMenu('btnFormatTypes');
        localStorage.setItem('admin_current_section', 'format-types');
        loadReference('format-types');
    };

    document.getElementById('btnAgeCategories').onclick = e => {
        e.preventDefault();
        setActiveMenu('btnAgeCategories');
        localStorage.setItem('admin_current_section', 'age-categories');
        loadReference('age-categories');
    };

    document.getElementById('btnExcursions').onclick = e => {
        e.preventDefault();
        setActiveMenu('btnExcursions');
        localStorage.setItem('admin_current_section', 'excursions');
        loadExcursions();
    };

    document.getElementById('btnNews').onclick = e => {
        e.preventDefault();
        setActiveMenu('btnNews');
        localStorage.setItem('admin_current_section', 'news');
        loadNewsTable();
    };

    document.getElementById('btnReservations').onclick = e => {
        e.preventDefault();
        setActiveMenu('btnReservations');
        localStorage.setItem('admin_current_section', 'reservation');
        loadReservations();
    };

    document.getElementById('btnTeam').onclick = e => {
        e.preventDefault();
        setActiveMenu('btnTeam');
        localStorage.setItem('admin_current_section', 'team');
        loadTeamSection();
    }

    document.getElementById('btnHome').onclick = e => {
        e.preventDefault()
        setActiveMenu('btnHome');
        localStorage.setItem('admin_current_section', 'home');
        loadHomeSection();
    }

    document.getElementById('btnProjects').onclick = e => {
        e.preventDefault();
        setActiveMenu('btnProjects');
        localStorage.setItem('admin_current_section', 'projects');
        loadProjectSection();
    }
    document.getElementById('btnHistory').onclick = e => {
        e.preventDefault();
        setActiveMenu('btnHistory');
        localStorage.setItem('admin_current_section', 'history');
        loadHistorySection();
    }

    document.getElementById('btnPartners').onclick = e => {
        e.preventDefault();
        setActiveMenu('btnPartners');
        localStorage.setItem('admin_current_section', 'partners');
        loadPartnersSection();
    }
    document.getElementById('btnRequisites').onclick = e => {
        e.preventDefault();
        setActiveMenu('btnRequisites');
        localStorage.setItem('admin_current_section', 'requisites');
        loadRequisitesSection();
    }

    const btnAddSession = document.getElementById('btnAddSession');
    const editingSessionId = document.getElementById('editingSessionId');
    const sessionDatetimeModal = document.getElementById('sessionDatetimeModal');
    const sessionCostModal = document.getElementById('sessionCostModal');
    const sessionMaxParticipantsModal = document.getElementById('sessionMaxParticipantsModal');

    btnAddSession.onclick = () => {
        editingSessionId.value = '';
        sessionDatetimeModal.value = '';
        sessionCostModal.value = '';
        sessionMaxParticipantsModal.value = '';

        const label = document.getElementById('sessionModalLabel');
        label.textContent = 'Добавить сессию';

        const icon = label.previousElementSibling;
        if (icon && icon.tagName === 'I') icon.style.display = 'inline-block';

        const header = document.querySelector('#sessionModal .modal-header');
        header.classList.remove('bg-primary', 'bg-opacity-10');
        header.classList.add('bg-success', 'bg-opacity-10');

        sessionModal.show();
    };


    const section = localStorage.getItem('admin_current_section');
    switch (section) {
        case 'users':
            setActiveMenu('btnUsers');
            loadUsers();
            break;
        case 'roles':
            setActiveMenu('btnRoles');
            loadReference('roles');
            break;
        case 'categories':
            setActiveMenu('btnCategories');
            loadReference('categories');
            break;
        case 'format-types':
            setActiveMenu('btnFormatTypes');
            loadReference('format-types');
            break;
        case 'age-categories':
            setActiveMenu('btnAgeCategories');
            loadReference('age-categories');
            break;
        case 'excursions':
            setActiveMenu('btnExcursions');
            loadExcursions();
            break;
        case 'news':
            setActiveMenu('btnNews');
            loadNewsTable();
            break;
        case 'reservation':
            setActiveMenu('btnReservations');
            loadReservations();
            break;
        case 'team':
            setActiveMenu('btnTeam');
            loadTeamSection();
            break;
        case 'home':
            setActiveMenu('btnHome');
            loadHomeSection();
            break;
        case 'projects':
            setActiveMenu('btnProjects');
            loadProjectSection();
            break;
        case 'history':
            setActiveMenu('btnHistory');
            loadHistorySection();
            break;
        case 'partners':
            setActiveMenu('btnPartners');
            loadPartnersSection();
            break;
        case 'requisites':
            setActiveMenu('btnRequisites');
            loadRequisitesSection();
            break;
        default:
            setActiveMenu('btnUsers');
            loadUsers();
            break;
    }
});
