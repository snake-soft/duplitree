document.body.addEventListener("htmx:configRequest", (event) => {
    event.detail.headers["X-CSRFToken"] = csrfToken;
});

function showModal() {
    const modal = new bootstrap.Modal(document.getElementById('modal'));
    modal.show();
}
