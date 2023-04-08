const imageFormatErrorElement = document.getElementById("imageFormatError");
const imageFormatError = imageFormatErrorElement ? JSON.parse(imageFormatErrorElement.textContent) : null;

function toastifyMessage(message) {
  if (imageFormatError != null) {
    Toastify({
      text: message,
      duration: 3000,
      gravity: "top",
      close: true,
      position: "right",
      stopOnFocus: true,
      style: {
        background: "linear-gradient(111.3deg, rgb(252, 56, 56) 11.7%, rgb(237, 13, 81) 81.7%)"
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
        background: "linear-gradient(to right, #e74694, #ff8a4c)"
      }
    }).showToast();
  }

}