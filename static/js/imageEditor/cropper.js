const image = document.getElementById("image-edit");
let cropper = null;

document.getElementById("crop-image")
        .addEventListener("click", function() {
  cropper = new Cropper(image, {
    aspectRatio: 1,
    viewMode: 1
  });
});

document.getElementById("apply-crop")
        .addEventListener("click", function() {
  const croppedCanvas = cropper.getCroppedCanvas();
  const croppedImage = new Image();
  croppedImage.src = croppedCanvas.toDataURL();
  // croppedCanvas.


  image.parentNode.replaceChild(croppedImage, image);
  cropper.destroy();
  cropper = null;
});