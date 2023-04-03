const modal = document.getElementById("modal");
const modalImg = document.getElementById("modal-img");
const infoImageModal = document.getElementById("defaultModal");

if (document.querySelector("[modal-backdrop]") !== null) {
  document.querySelector("[modal-backdrop]").setAttribute("class", "hidden bg-gray-900 bg-opacity-50 dark:bg-opacity-80 fixed inset-0 z-40");
}

function showImageModal(src) {
  modal.classList.remove("hidden");
  modalImg.src = src;
}

function closeImageModal() {
  modal.classList.add("hidden");
}

function showInfoImageModal() {
  infoImageModal.classList.remove("hidden");
  if (document.querySelector("[modal-backdrop]") !== null) {
    document.querySelector("[modal-backdrop]").setAttribute("class", "bg-gray-900 bg-opacity-50 dark:bg-opacity-80 fixed inset-0 z-40");
  }
}

function closeInfoImageModal() {
  infoImageModal.classList.add("hidden");
  if (document.querySelector("[modal-backdrop]") !== null) {
    document.querySelector("[modal-backdrop]").setAttribute("class", "hidden bg-gray-900 bg-opacity-50 dark:bg-opacity-80 fixed inset-0 z-40");
  }
}

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape" || event.key === "Esc") {
    closeImageModal();
    closeInfoImageModal();
  }
});