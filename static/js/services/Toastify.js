function toastifyMessage(message, success) {
  Toastify({
    text: message,
    duration: 5000,
    gravity: "top",
    close: true,
    position: "right",
    stopOnFocus: true,
    style: {
      background: success === true ? "linear-gradient(to top, #9be15d 0%, #00e3ae 100%)" : "#FF0000",
      borderRadius: "10px"
    }
  }).showToast();
}
