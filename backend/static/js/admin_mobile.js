function initAdminMobileNavigation() {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.getElementById('adminMenuToggle');
    const close = document.getElementById('adminNavClose');
    const backdrop = document.getElementById('adminNavBackdrop');
    const content = document.getElementById('mainContent');
    if (!sidebar || !toggle || !close || !backdrop || !content || sidebar.dataset.mobileReady) return;
    sidebar.dataset.mobileReady = 'true';
    const mobile = window.matchMedia('(max-width: 768px)');
    let opened = false;
    let previousOverflow = '';

    function setOpen(value, returnFocus = false) {
        const wasOpen = opened;
        opened = value && mobile.matches;
        sidebar.classList.toggle('show', opened);
        sidebar.inert = mobile.matches && !opened;
        sidebar.setAttribute('aria-hidden', String(mobile.matches && !opened));
        toggle.setAttribute('aria-expanded', String(opened));
        toggle.setAttribute('aria-label', opened ? 'Закрыть меню' : 'Открыть меню');
        backdrop.hidden = !opened;
        content.inert = opened;
        if (opened && !wasOpen) {
            previousOverflow = document.body.style.overflow;
            document.body.style.overflow = 'hidden';
            (sidebar.querySelector('.nav-link.active') || close).focus();
        } else if (!opened && wasOpen) {
            document.body.style.overflow = previousOverflow;
            if (returnFocus) toggle.focus();
        }
    }
    toggle.onclick = () => setOpen(!opened, true);
    close.onclick = () => setOpen(false, true);
    backdrop.onclick = () => setOpen(false, true);
    sidebar.addEventListener('click', event => {
        if (opened && event.target.closest('.nav-link')) {
            setOpen(false);
            document.getElementById('pageTitle')?.focus();
        }
    });
    document.addEventListener('keydown', event => {
        if (!opened) return;
        if (event.key === 'Escape') { event.preventDefault(); setOpen(false, true); }
        if (event.key !== 'Tab') return;
        const items = [...sidebar.querySelectorAll('button, a[href]')].filter(item => !item.disabled && !item.hidden);
        const first = items[0], last = items.at(-1);
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    });
    mobile.addEventListener('change', () => {
        setOpen(false);
        document.querySelectorAll('[data-mobile-details]').forEach(details => {
            details.open = !mobile.matches || details.dataset.active === 'true';
        });
    });
    setOpen(false);
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initAdminMobileNavigation);
else initAdminMobileNavigation();
