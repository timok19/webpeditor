const imageFormatErrorElement = document.getElementById("imageFormatError");
const imageFormatError = imageFormatErrorElement ? JSON.parse(imageFormatErrorElement.textContent) : null;

function toastifyMessage(message, success) {
  if (imageFormatError != null || success === false) {
    Toastify({
      text: message,
      duration: 3000,
      gravity: "top",
      close: true,
      position: "right",
      stopOnFocus: true,
      style: {
        background: "#FF0000"
      }
    }).showToast();
  } else {
    Toastify({
      text: message,
      duration: 3000,
      gravity: "top",
      close: true,
      position: "right",
      stopOnFocus: true,
      style: {
        background: "linear-gradient(to top, #9be15d 0%, #00e3ae 100%)",
      }
    }).showToast();
  }
}