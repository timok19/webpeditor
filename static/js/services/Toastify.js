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
        background: "linear-gradient(to right, #43e97b 0%, #38f9d7 100%)",
      }
    }).showToast();
  }

}