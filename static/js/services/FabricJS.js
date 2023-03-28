const imageUrl = JSON.parse(document.getElementById("imageUrl").textContent);

const canvas = new fabric.Canvas('image-editor');

fabric.Image.fromURL(`${imageUrl}`, img => {
  img.scaleToWidth(canvas.width);
  img.scaleToHeight(canvas.height);
  canvas.add(img);
  canvas.renderAll();
});