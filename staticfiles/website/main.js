function setReceiverId(userId) {
    document.getElementById('receiver_in_modal').value = userId;
}

function forceAdd() {
    document.getElementById("save_edit_form").reset();
    document.getElementById("editingFlag").value = "";
}

const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
