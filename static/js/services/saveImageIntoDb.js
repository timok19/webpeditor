const csrfToken = JSON.parse(document.getElementById("csrfToken").textContent);
const editedImageFormId = JSON.parse(document.getElementById("editedImageFormId").textContent)

async function saveImage() {
  const imageInput = document.getElementById(editedImageFormId);

  const formData = new FormData();
  formData.append("image", imageInput.files[0]);

  const response = await fetch('/image_edit/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrfToken
    },
    body: formData
  });

  if (response.ok) {
    const jsonResponse = await response.json();
    console.log(jsonResponse);
  } else {
    console.error('Error uploading image');
  }
}