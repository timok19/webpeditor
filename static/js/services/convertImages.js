const csrfTokenElement = document.getElementsByName("csrfmiddlewaretoken")[0];
const csrfToken = csrfTokenElement ? csrfTokenElement.value : null;

const inputIdElement = document.getElementById("inputId");
const inputId = inputIdElement ? JSON.parse(inputIdElement.textContent) : null;

const outputFormatIdElement = document.getElementById("outputFormatId");
const outputFormatId = inputIdElement ? JSON.parse(outputFormatIdElement.textContent) : null;

const uploadAndConvertButton = document.getElementById("upload-image");
uploadAndConvertButton.addEventListener("click", () => uploadAndConvert())

function uploadAndConvert() {
  const form = document.getElementById('imageFormConvertId');
  form.addEventListener("submit", (event) => event.preventDefault());

  const formData = new FormData();
  const imageFiles = document.getElementById(`${inputId}`).files;

  for (let i = 0; i < imageFiles.length; i++) {
    formData.append('images_to_convert', imageFiles[i]);
  }

  const outputFormat = document.getElementById(`${outputFormatId}`).value;
  formData.append('output_format', outputFormat);

  fetch('/api/image_convert/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrfToken
    },
    body: formData,
  })
    .then(response => {
      if (response.status === 400 || response.status === 500) {
        throw new Error('An error occurred while processing the images');
      }
      return response.blob();
    })
    .then(data => {
      if (data.status === 'error') {
        toastifyMessage(data.message, false);
        location.reload()
      } else {
        toastifyMessage('Images has been converted', true);
        location.reload()
      }
    })
    .catch(error => {
      toastifyMessage(error.message, false);
      location.reload()
    });
}
