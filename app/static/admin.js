function openModal(id) {
    document.getElementById(id).style.display = "block";
}

function closeModal() {
    document.querySelectorAll(".modal").forEach(m => {
        m.style.display = "none";
    });
}
