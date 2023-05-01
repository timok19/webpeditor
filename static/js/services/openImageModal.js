const modal = document.getElementById("modal-image");

const imageIdElement = document.getElementById("imageId");
let imageId = imageIdElement ? JSON.parse(imageIdElement.textContent) : null;
const image = document.getElementById(imageId)

if (document.querySelector("[modal-backdrop]") !== null) {
  document.querySelector("[modal-backdrop]").setAttribute("class", "hidden bg-gray-900 bg-opacity-50 dark:bg-opacity-80 fixed inset-0 z-40");
}

function showImageModal(src) {
  console.log(src)
  modal.classList.remove("hidden");
  image.src = src;
}

function closeImageModal() {
  modal.classList.add("hidden");
}

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape" || event.key === "Esc") {
    closeImageModal();
  }
});