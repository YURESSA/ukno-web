const modal = document.getElementById('excursionModal');

function closeModal() {
    modal.style.display = 'none';
}

document.getElementById('modalClose').onclick = closeModal;
document.getElementById('modalCloseFooter').onclick = closeModal;
window.onclick = (event) => {
    if (event.target === modal) {
        closeModal();
    }
};