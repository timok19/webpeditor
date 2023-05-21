function showProgressBarAndMessage(message, success) {
  let i = 0;
  if (i === 0) {
    i = 1;
    const progressBar = document.getElementById("progress-bar-container")
    progressBar.style.display = "inline-block";
    const bar = document.getElementById("bar");
    bar.style.visibility = "visible";

    let width = 1;
    const id = setInterval(frame, 10);

    function frame() {
      if (width >= 100) {
        clearInterval(id);
        i = 0;
      } else {
        width++;
        bar.style.width = width + "%";
      }
    }
  }
  toastifyMessage(message, success);
}