const imageInput = document.querySelector("input[type='file']");
const uploadImageButton = document.querySelector("#upload-image");
imageInput.addEventListener("change", function() {
    if (imageInput.value) {
        uploadImageButton.classList.remove('cursor-not-allowed')
        uploadImageButton.disabled = false;
    } else {
        uploadImageButton.classList.add('cursor-not-allowed')
    }
})