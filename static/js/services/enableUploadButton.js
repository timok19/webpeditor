const imageInput = document.querySelector("input[type='file']");
const uploadImageButton = document.getElementById("upload-image");

const qualityElement = document.getElementById("id_quality")

imageInput.addEventListener("change", function() {
    const cursorNotAllowedClass = 'cursor-not-allowed';
    if (imageInput.value) {
        uploadImageButton.classList.remove(cursorNotAllowedClass)
        uploadImageButton.disabled = false;
        qualityElement.classList.remove(cursorNotAllowedClass)
        qualityElement.classList.add('cursor-pointer')
        qualityElement.disabled = false;
    } else {
        uploadImageButton.classList.add(cursorNotAllowedClass)
    }
})