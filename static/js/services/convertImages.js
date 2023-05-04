const csrfTokenElement = document.getElementsByName("csrfmiddlewaretoken")[0];
const csrfToken = csrfTokenElement ? csrfTokenElement.value : null;

const inputIdElement = document.getElementById("inputId");
const inputId = inputIdElement ? JSON.parse(inputIdElement.textContent) : null;

const outputFormatIdElement = document.getElementById("outputFormatId");
const outputFormatId = inputIdElement ? JSON.parse(outputFormatIdElement.textContent) : null;

const form = document.getElementById('imageFormConvertId');
const outputFormatInput = document.getElementById(`${outputFormatId}`);
const imageFilesInput = document.getElementById(`${inputId}`);

const uploadAndConvertButton = document.getElementById("upload-image");
uploadAndConvertButton.addEventListener("click", () => uploadAndConvert());

const downloadConvertedButton = document.getElementById("download-converted");
downloadConvertedButton.addEventListener("click", () => getImagesFromDb())

function uploadAndConvert() {
  form.addEventListener("submit", (event) => event.preventDefault());

  const maxFileSize = 6_000_000;

  const formData = new FormData();
  const imageFiles = imageFilesInput.files;

  if (imageFiles.length <= 15) {
    for (let i = 0; i < imageFiles.length; i++) {
      if (imageFiles[i].size <= maxFileSize) {
        formData.append('images_to_convert', imageFiles[i]);
      } else {
        showProgressBarAndMessage(`Error, file size should not exceed ${maxFileSize / 1_000_000} MB`, false);
        location.reload();
      }
    }
    const outputFormat = outputFormatInput.value;
    formData.append('output_format', outputFormat);
    showProgressBarAndMessage("Uploading image(s)...", true);

  } else {
    showProgressBarAndMessage("Error, number of files to upload should not exceed 15", false);
    location.reload();
  }

  fetch('/api/image_convert/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrfToken
    },
    body: formData,
  })
    .then(response => {
      if (response.status === 400 || response.status === 500) {
        toastifyMessage('Error: something unexpected happened', false);
        location.reload()
        throw new Error('An error occurred while processing the images');
      }
      return response.blob();
    })
    .then(_ => {
      toastifyMessage('Image(s) has been converted', true);
      location.reload()
    })
    .catch(error => {
      toastifyMessage(error.message, false);
      location.reload()
    });
}

function getImagesFromDb() {
  let imageUrl = "";
  let imageName = "";
  
  fetch("/api/image_download_converted/", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Failed to fetch the converted image");
      }
      return response.json();
    })
    .then((data) => {
      imageUrl = data["image_url"];
      imageName = data["image_name"];
      downloadConvertedImage(imageUrl, imageName);
    })
    .catch((error) => {
      console.error("There was a problem with the fetch operation:", error);
    });
}

function downloadConvertedImage(imageUrl, imageName) {
  fetch(imageUrl).then((response) => {
    if (response.status !== 200) {
      throw new Error(`Unable to download file. HTTP status: ${response.status}`);
    }
    return response.blob();
  }).then((blob) => {
    saveAs(blob, imageName);
    toastifyMessage("Converted image has been downloaded", true);
  }).catch((error) => {
    console.error("There was a problem with the fetch operation:", error);
    toastifyMessage("Failed to download converted image", false);
  })
}