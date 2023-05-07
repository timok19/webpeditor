const csrfTokenElement = document.getElementsByName("csrfmiddlewaretoken")[0];
const csrfToken = csrfTokenElement ? csrfTokenElement.value : null;

const form = document.getElementById('imageFormConvertId');
const outputFormatInput = document.getElementById("id_output_format");
const imageFilesInput = document.getElementById("id_images_to_convert");
const qualityIdInput = document.getElementById("id_quality");

const uploadAndConvertButton = document.getElementById("upload-image");
uploadAndConvertButton.addEventListener("click", () => uploadAndConvert());

document.addEventListener("DOMContentLoaded", () => {
  getImagesFromDb();
})

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
    const quality = qualityIdInput.value;
    formData.append('output_format', outputFormat);
    formData.append('quality', quality);
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
        throw new Error('Error: After converting image(s), one or more file has size more than 6 MB');
      }
      return response.blob();
    })
    .then(_ => {
      toastifyMessage('Image(s) has been converted', true);
      location.reload()
    })
    .catch(error => {
      toastifyMessage(error.message, false);
      setTimeout(function () {
        location.reload()
      }, 5000)
    });
}

function getImagesFromDb() {
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
      const downloadAllConvertedButtonId = "download-all-converted";
      const downloadAllConvertedButton = document.getElementById(downloadAllConvertedButtonId)
      const convertedImages = data["converted_images"]
      setupPopoverListeners(convertedImages)

      if (downloadAllConvertedButton) {
        downloadAllConvertedButton.addEventListener("click", () => {
          getZipUrl()
        })
      }
    })
    .catch((error) => {
      console.error("There was a problem with the fetch operation:", error);
    });
}

function setupPopoverListeners(convertedImages) {
  for (let i = 0; i < convertedImages.length; i++) {
    const imageUrl = convertedImages[i][0];
    const imageName = convertedImages[i][1];
    const publicId = convertedImages[i][2];
    const imageNameShorter = convertedImages[i][3];

    const downloadButtonId = `download-button-${imageNameShorter}`;
    const downloadButton = document.getElementById(downloadButtonId);

    const deleteButtonId = `delete-button-${imageNameShorter}`;
    const deleteButton = document.getElementById(deleteButtonId);

    const tableRowId = `table-row-${imageNameShorter}`;

    if (downloadButton) {
      downloadButton.addEventListener("click", () => {
        downloadConvertedImage(imageUrl, imageName);
      });
    }

    if (deleteButton) {
      deleteButton.addEventListener("click", () => {
        deleteConvertedImage(publicId, deleteButtonId, tableRowId)
          .then(() => {
            const remainingRows = $('table#converted-images-table tr').length - 1;
            if (remainingRows === 0) {
              $("#converter").load(location.href + " #converter");
            }
          });
      });
    }
  }
}

function downloadConvertedImage(imageUrl, imageName) {
  fetch(imageUrl)
    .then((response) => {
      if (response.status !== 200) {
        throw new Error(`Unable to download file. HTTP status: ${response.status}`);
      }
      return response.blob();
    })
    .then((blob) => {
      saveAs(blob, imageName);
      toastifyMessage("Converted image has been downloaded", true);
    })
    .catch((error) => {
      console.error("There was a problem with the fetch operation:", error);
      toastifyMessage("Failed to download converted image", false);
    })
}

function deleteConvertedImage(publicId, deleteButtonId, tableRowId) {
  return fetch("/api/image_delete_converted/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      public_id: publicId
    }),
  })
    .then((response) => {
      if (!response.ok || response.status !== 200) {
        throw new Error(`Unable to delete file. HTTP status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      const successMessage = data["message"];
      toastifyMessage(successMessage, true);
      $(`[id='${deleteButtonId}']`).closest(`[id='${tableRowId}']`).remove();
    })
    .catch((error) => {
      console.error("There was a problem with the fetch operation:", error);
      toastifyMessage("Failed to delete converted image", false);
    })
}

function getZipUrl() {
  fetch("/api/download_all_converted/", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Failed to fetch the ZIP file. HTTP status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      const url = data["zip_url"]
      downloadAllConvertedImages(url)
    })
    .catch((error) => {
      console.error("There was a problem with the fetch operation:", error);
      toastifyMessage("Failed to download zip with converted images", false);
    })
}

function downloadAllConvertedImages(url) {
  fetch(url)
    .then((response) => {
      if (response.status !== 200) {
        throw new Error(`Unable to download zip file. HTTP status: ${response.status}`);
      }
      return response.blob();
    })
    .then((blob) => {
      saveAs(blob, "webpeditor_converted_images.zip")
      toastifyMessage("Zip with converted images has been downloaded", true);
    })
    .catch((error) => {
      console.error("There was a problem with the fetch operation:", error);
      toastifyMessage("Failed to download converted image", false);
    })
}
