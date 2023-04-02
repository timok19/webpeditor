document.addEventListener("DOMContentLoaded", function() {
  const ImageEditor = tui.ImageEditor;
  const container = document.querySelector("#tui-image-editor");

  const imageUrl = JSON.parse(document.getElementById("imageUrl").textContent);
  const imageContentType = JSON.parse(document.getElementById("imageContentType").textContent);
  const imageName = JSON.parse(document.getElementById("imageName").textContent);

  const editor = new ImageEditor(container, {
    includeUI: {
      loadImage: {
        path: imageUrl,
        name: imageName
      }, theme: {
        "common.backgroundImage": "none",
        "common.backgroundColor": "transparent"
      }, menu: ["resize", "crop", "flip", "rotate", "draw", "shape", "icon", "text", "mask", "filter"],
      uiSize: {
        width: "50rem",
        height: "40rem"
      },
      menuBarPosition: "left"
    },
    cssMaxWidth: 700,
    cssMaxHeight: 500,
    usageStatistics: false,
    selectionStyle: {
      cornerSize: 20,
      rotatingPointOffset: 70
    }
  });

  // Delete Upload button
  document.querySelector(".tui-image-editor-header-buttons div").remove();

  // Icon svg (Download button)
  const svgDownloadIcon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svgDownloadIcon.setAttribute("fill", "none");
  svgDownloadIcon.setAttribute("stroke-width", "1.5");
  svgDownloadIcon.setAttribute("viewBox", "0 0 24 24");
  svgDownloadIcon.setAttribute("stroke", "currentColor");
  svgDownloadIcon.setAttribute("aria-hidden", "true");
  svgDownloadIcon.setAttribute("class", "w-6 h-6 ml-1 mr-1");

  // Path icon (Download button)
  const svgDownloadPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
  svgDownloadPath.setAttribute("stroke-linecap", "round");
  svgDownloadPath.setAttribute("stroke-linejoin", "round");
  svgDownloadPath.setAttribute("fill-rule", "evenodd");
  svgDownloadPath.setAttribute("clip-rule", "evenodd");
  svgDownloadPath.setAttribute("d", "M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 " + "1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m.75 12l3 3m0 0l3-3m-3 3v-6m-1.5-9H5.625c-.621 " + "0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z");
  svgDownloadIcon.appendChild(svgDownloadPath);

  // Icon svg (Save button)
  const svgSaveIcon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svgSaveIcon.setAttribute("fill", "none");
  svgSaveIcon.setAttribute("stroke-width", "2");
  svgSaveIcon.setAttribute("viewBox", "0 0 24 24");
  svgSaveIcon.setAttribute("stroke", "currentColor");
  svgSaveIcon.setAttribute("aria-hidden", "true");
  svgSaveIcon.setAttribute("class", "w-6 h-6 ml-1 mr-1");

  // Path icon (Save button)
  const svgSavePath = document.createElementNS("http://www.w3.org/2000/svg", "path");
  svgSavePath.setAttribute("stroke-linecap", "round");
  svgSavePath.setAttribute("stroke-linejoin", "round");
  svgSavePath.setAttribute("d", "M4.5 12.75l6 6 9-13.5");
  svgSaveIcon.appendChild(svgSavePath);

  const oldDownloadButton = document.querySelector(".tui-image-editor-header-buttons button");
  oldDownloadButton.style.display = "none";

  let downloadButton = document.createElement("button");
  downloadButton.addEventListener("click", () => downloadImage(imageContentType, 1, imageName));
  downloadButton.id = "tuiDownloadButton";
  downloadButton.className = "relative inline-flex items-center justify-center p-0.5 mb-2 mr-2 ml-2 mt-2 overflow-hidden " + "text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-pink-500 to-orange-400 " + "group-hover:from-pink-500 group-hover:to-orange-400 hover:text-white dark:text-white focus:ring-4 " + "focus:outline-none focus:ring-pink-200 dark:focus:ring-pink-800 text-center";
  downloadButton.appendChild(addSpanTextToButton("Download image"));
  downloadButton.appendChild(svgDownloadIcon);

  // Save button
  let saveButton = document.createElement("button");
  saveButton.addEventListener("click", () => saveImage(imageContentType, 1, imageName));
  saveButton.id = "tuiSaveButton";
  saveButton.className = "relative inline-flex items-center justify-center p-0.5 mb-2 mr-2 ml-2 mt-2 overflow-hidden " + "text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-pink-500 to-orange-400 " + "group-hover:from-pink-500 group-hover:to-orange-400 hover:text-white dark:text-white focus:ring-4 " + "focus:outline-none focus:ring-pink-200 dark:focus:ring-pink-800 text-center";
  saveButton.appendChild(addSpanTextToButton("Save image"));
  saveButton.appendChild(svgSaveIcon);

  // Div with Save button
  const newDiv = document.createElement("div");
  oldDownloadButton.parentNode.insertBefore(newDiv, oldDownloadButton);
  newDiv.appendChild(downloadButton);
  newDiv.appendChild(saveButton);
  newDiv.style.display = "flex";
  newDiv.style.justifyContent = "center";
  newDiv.style.paddingTop = "0.5rem";
  newDiv.style.paddingRight = "0.5rem";

  const imageEditorWrap = document.querySelector(".tui-image-editor-wrap");
  imageEditorWrap.style.bottom = "0";
  imageEditorWrap.style.top = "0";
  imageEditorWrap.style.left = "0";
  imageEditorWrap.style.width = "85%";

  const imageEditor = document.querySelector("#tui-image-editor");
  imageEditor.style.width = "52rem";
  imageEditor.style.height = "36rem";

  const subItemMaskChoice = document.querySelector(".tui-image-editor-menu-mask ul.tui-image-editor-submenu-item");
  subItemMaskChoice.style.marginTop = "0.5rem";
  subItemMaskChoice.style.background = "transparent";

  const menuFilter = document.querySelector(".tui-image-editor-menu-filter");
  menuFilter.style.padding = "1rem";
  menuFilter.style.height = "100%";

  const imageEditorContainer = document.querySelector("#tui-image-editor");
  imageEditorContainer.style.borderRadius = "1rem";
  imageEditorContainer.style.background = "#1F2937";

  editCanvasSize(".lower-canvas");
  editCanvasSize(".upper-canvas");

  const submenuStyle = document.querySelector(".tui-image-editor-submenu-style");
  submenuStyle.style.backgroundColor = "#1e1e1e";

  const submenuEl = document.querySelector(".tui-image-editor-submenu");
  submenuEl.style.height = "600px";

  // Deleting logo
  document.querySelector(".tui-image-editor-header-logo").remove();

  // Main controllers
  document.querySelector(".tui-image-editor-controls").style.backgroundColor = "transparent";

  // Top menu buttons
  const topButtons = document.querySelector(".tui-image-editor-header div.tui-image-editor-header-buttons");
  topButtons.removeAttribute("class");

  // Help menu
  const helpMenu = document.querySelector("ul.tui-image-editor-help-menu");
  helpMenu.style.marginTop = "0.1rem";
  helpMenu.style.borderRadius = "0.4rem";
  helpMenu.style.background = "transparent";
  helpMenu.style.position = "absolute";

  const imageEditorMainContainer = document.querySelector(".tui-image-editor-main-container");
  imageEditorMainContainer.style.width = "calc(100% - 120px)";

  // Span with text and icon
  function addSpanTextToButton(textOnButton) {
    const spanText = document.createElement("span");
    spanText.className = "relative px-2 py-2 transition-all ease-in duration-75 bg-white dark:bg-gray-900 " + "rounded-md group-hover:bg-opacity-0 text-center inline-flex items-center";
    spanText.textContent = textOnButton + String.fromCharCode(160);
    return spanText;
  }

  function editCanvasSize(queryClass) {
    const canvas = document.querySelector(queryClass);
    canvas.style.position = "absolute";
    canvas.style.width = "400px";
    canvas.style.height = "400px";
    canvas.style.left = "-20px";
    canvas.style.top = "0";
    canvas.style.touchAction = "none";
    canvas.style.userSelect = "none";
    canvas.style.maxWidth = "480px";
    canvas.style.maxHeight = "550px";

    if (queryClass === ".upper-canvas") {
      canvas.style.cursor = "zoom-in";
    }
  }

  function dataURLtoBlob(mimeType, quality) {
    const dataURL = editor.toDataURL({
      format: mimeType,
      quality: quality
    });

    const data = atob(dataURL.split(",")[1]);
    const arrayBuffer = new ArrayBuffer(data.length);
    const view = new Uint8Array(arrayBuffer);
    for (let i = 0; i < data.length; i++) {
      view[i] = data.charCodeAt(i) & 0xff;
    }
    return new Blob([arrayBuffer], { type: mimeType });
  }

  function downloadImage(mimeType, quality, filename) {
    const editedImageForm = document.getElementById("editedImageFormId");
    editedImageForm.addEventListener("submit", (event) => event.preventDefault());

    const blob = dataURLtoBlob(mimeType, quality);
    console.log(blob);
    saveAs(blob, filename);
  }

  function saveImage(mimeType, quality, fileName) {
    const csrfToken = JSON.parse(document.getElementById("csrfToken").textContent);
    // const csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']").val();
    console.log(csrfToken)

    const editedImageForm = document.getElementById("editedImageFormId");
    editedImageForm.addEventListener("submit", (event) => event.preventDefault());

    const imageBlob = dataURLtoBlob(mimeType, quality);

    const formData = new FormData();
    formData.append("edited_image_file", imageBlob, fileName);

    fetch("/image_edit/", {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfToken
      },
      body: formData
    }).then((response) => {
      console.log(response)
      if (response.ok) {
        console.log("Success");
      } else {
        console.error("Error");
      }
    });
  }
});