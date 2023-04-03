function toastifyMessage(message) {
  Toastify({
    text: message,
    duration: 3000,
    gravity: "top",
    close: true,
    position: "right",
    stopOnFocus: true,
    style: {
      background: "linear-gradient(to right, #e74694, #ff8a4c)"
    }
  }).showToast();
}