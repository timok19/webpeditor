import Toastify from 'toastify-js'
import "toastify-js/src/toastify.css";

const submitButton = document.getElementById("submit-uploading-image");

submitButton.addEventListener("click", function () {
  Toastify({
    text: "This is a toast",
    duration: 3000,
    newWindow: true,
    close: true,
    gravity: "top",
    position: "center",
    stopOnFocus: true,
    style: {
      background: "linear-gradient(to right, #00b09b, #96c93d)"
    },
  }).showToast();
});

