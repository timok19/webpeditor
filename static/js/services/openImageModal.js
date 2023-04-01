const modal = document.getElementById("modal");
const modalImg = document.getElementById("modal-img");

function showModal(src) {
  modal.classList.remove("hidden");
  modalImg.src = src;
}

function closeModal() {
  modal.classList.add("hidden");
}

window.addEventListener("keydown", (event) => {
  // Check if the pressed key is the "Esc" or "Escape" key
  if (event.key === "Escape" || event.key === "Esc") {
    closeModal();
  }
});