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
        background: "linear-gradient(110.1deg, rgb(34, 126, 34) 2.9%, rgb(168, 251, 60) 90.3%)",
      }
    }).showToast();
  }

}