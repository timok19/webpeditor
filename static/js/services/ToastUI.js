document.addEventListener("DOMContentLoaded", function() {
  const ImageEditor = tui.ImageEditor;
  const container = document.querySelector("#tui-image-editor");

  const csrfTokenElement = document.getElementById("csrfToken");
  const csrfToken = csrfTokenElement ? JSON.parse(csrfTokenElement.textContent) : null;

  const imageUrlElement = document.getElementById("imageUrl");
  const imageUrl = imageUrlElement ? JSON.parse(imageUrlElement.textContent) : null;

  const imageContentTypeElement = document.getElementById("imageContentType");
  const imageContentType = imageContentTypeElement ? JSON.parse(imageContentTypeElement.textContent) : null;

  const imageNameElement = document.getElementById("imageName");
  const imageName = imageNameElement ? JSON.parse(imageNameElement.textContent) : null;

  const maxImageBlobSize = 6291456;

  const editor = new ImageEditor(container, {
    includeUI: {
      loadImage: {
        path: imageUrl,
        name: imageName
      }, theme: {
        "common.backgroundImage": "none",
        "common.backgroundColor": "transparent"
      }, menu: [
        "resize",
        "crop",
        "flip",
        "rotate",
        "draw",
        "shape",
        "icon",
        "text",
        "mask",
        "filter"
      ],
      uiSize: {
        width: "52rem",
        height: "36rem"
      },
      menuBarPosition: "left"
    },
    cssMaxWidth: "700",
    cssMaxHeight: "500",
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
  svgDownloadPath.setAttribute("d", "M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 " +
      "1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m.75 12l3 3m0 0l3-3m-3 3v-6m-1.5-9H5.625c-.621 " +
      "0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z");
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

  // Icon svg (Return original image)
  const svgOriginalImageIcon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svgOriginalImageIcon.setAttribute("fill", "none");
  svgOriginalImageIcon.setAttribute("stroke-width", "1.5");
  svgOriginalImageIcon.setAttribute("viewBox", "0 0 24 24");
  svgOriginalImageIcon.setAttribute("stroke", "currentColor");
  svgOriginalImageIcon.setAttribute("aria-hidden", "true");
  svgOriginalImageIcon.setAttribute("class", "w-6 h-6 ml-1 mr-1");

  // Path icon (Return original image)
  const svgOriginalImagePath = document.createElementNS("http://www.w3.org/2000/svg", "path");
  svgOriginalImagePath.setAttribute("stroke-linecap", "round");
  svgOriginalImagePath.setAttribute("stroke-linejoin", "round");
  svgOriginalImagePath.setAttribute("d", "M9 15L3 9m0 0l6-6M3 9h12a6 6 0 010 12h-3");
  svgOriginalImageIcon.appendChild(svgOriginalImagePath);

  // Old download button
  const oldDownloadButton = document.querySelector(".tui-image-editor-header-buttons button");
  oldDownloadButton.style.display = "none";

  // Download button
  let downloadButton = document.createElement("button");
  downloadButton.addEventListener("click", () => downloadImage(imageContentType, 1, imageName));
  downloadButton.id = "tuiDownloadButton";
  downloadButton.className = "relative inline-flex items-center justify-center p-0.5 mb-2 mr-2 ml-2 mt-2 overflow-hidden " +
      "text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-pink-500 to-orange-400 " +
      "group-hover:from-pink-500 group-hover:to-orange-400 hover:text-white dark:text-white focus:ring-4 " +
      "focus:outline-none focus:ring-pink-200 dark:focus:ring-pink-800 text-center";
  downloadButton.appendChild(addSpanTextToButton("Download image"));
  downloadButton.appendChild(svgDownloadIcon);

  // Save button
  let saveButton = document.createElement("button");
  saveButton.addEventListener("click", () => saveImage(imageContentType, 1, imageName));
  saveButton.id = "tuiSaveButton";
  saveButton.className = "relative inline-flex items-center justify-center p-0.5 mb-2 mr-2 ml-2 mt-2 overflow-hidden " +
      "text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-pink-500 to-orange-400 " +
      "group-hover:from-pink-500 group-hover:to-orange-400 hover:text-white dark:text-white focus:ring-4 " +
      "focus:outline-none focus:ring-pink-200 dark:focus:ring-pink-800 text-center";
  saveButton.appendChild(addSpanTextToButton("Save image"));
  saveButton.appendChild(svgSaveIcon);

  let originalImageButton = document.createElement("button");
  // saveButton.addEventListener("click", () => saveImage(imageContentType, 1, imageName));
  originalImageButton.id = "tuiOriginalImageButton";
  originalImageButton.className = "relative inline-flex items-center justify-center p-0.5 mb-2 mr-2 ml-2 mt-2 overflow-hidden " +
      "text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-pink-500 to-orange-400 " +
      "group-hover:from-pink-500 group-hover:to-orange-400 hover:text-white dark:text-white focus:ring-4 " +
      "focus:outline-none focus:ring-pink-200 dark:focus:ring-pink-800 text-center";
  originalImageButton.appendChild(addSpanTextToButton("Return original image"));
  originalImageButton.appendChild(svgOriginalImageIcon);


  // Additional div to group 2 buttons
  const twoButtonsDiv = document.createElement("div");
  twoButtonsDiv.appendChild(downloadButton);
  twoButtonsDiv.appendChild(saveButton);
  twoButtonsDiv.className = "flex justify-center items-center space-x-2";

  // Div with Download and Save buttons
  const newDiv = document.createElement("div");
  oldDownloadButton.parentNode.insertBefore(newDiv, oldDownloadButton);
  newDiv.appendChild(originalImageButton);
  newDiv.appendChild(twoButtonsDiv);
  newDiv.style.marginTop = "0.2rem";
  newDiv.style.marginRight = "0.8rem";
  newDiv.className = "flex justify-between items-center";

  const imageEditorWrap = document.querySelector(".tui-image-editor-wrap");
  imageEditorWrap.style.bottom = "0";
  imageEditorWrap.style.top = "0";
  imageEditorWrap.style.left = "0";
  imageEditorWrap.style.width = "85%";

  const subItemMaskChoice = document.querySelector(".tui-image-editor-menu-mask ul.tui-image-editor-submenu-item");
  subItemMaskChoice.style.marginTop = "0.5rem";
  subItemMaskChoice.style.background = "transparent";

  const menuFilter = document.querySelector(".tui-image-editor-menu-filter");
  menuFilter.style.padding = "1rem";
  menuFilter.style.height = "100%";

  // Svg icon (Show image info button)
  const svgImageInfoIcon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svgImageInfoIcon.setAttribute("fill", "none");
  svgImageInfoIcon.setAttribute("stroke", "currentColor");
  svgImageInfoIcon.setAttribute("stroke-width", "1.2");
  svgImageInfoIcon.setAttribute("viewBox", "0 0 24 24");
  svgImageInfoIcon.setAttribute("aria-hidden", "true");
  svgImageInfoIcon.setAttribute("class", "w-6 h-6 ml-1 mr-1 text-gray-400 hover:text-gray-500");

  // Path icon (Show image info button)
  const svgImageInfoPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
  svgImageInfoPath.setAttribute("stroke-linecap", "round");
  svgImageInfoPath.setAttribute("stroke-linejoin", "round");
  svgImageInfoPath.setAttribute("d", "M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z");
  svgImageInfoIcon.appendChild(svgImageInfoPath);

  // Image info popover button
  let imageInfoButton = document.createElement("button");
  imageInfoButton.setAttribute("data-popover-target", "popover-description");
  imageInfoButton.setAttribute("data-popover-placement", "left");
  imageInfoButton.setAttribute("type", "button");
  imageInfoButton.style.marginBottom = "2rem";
  imageInfoButton.appendChild(svgImageInfoIcon)

  let menu = document.querySelector(".tui-image-editor-menu");
  menu.insertBefore(imageInfoButton, menu.firstElementChild);

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

  function preventFormFromDefaultAction() {
    const editedImageForm = document.getElementById("editedImageFormId");
    editedImageForm.addEventListener("submit", (event) => event.preventDefault());
  }

  function downloadImage(mimeType, quality, fileName) {
    preventFormFromDefaultAction();

    const imageBlob = dataURLtoBlob(mimeType, quality);

    if (imageBlob.size > maxImageBlobSize) {
      toastifyMessage("Failed to download. Image size cannot be more than 6 MB", false);
    } else {
      const formData = new FormData();
      formData.append("image_file", imageBlob, fileName);
      formData.append("mime_type", mimeType);

      fetch("/image_download/", {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
        },
        body: formData
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }

          return response.blob();
        })
        .then((convertedBlob) => {
          saveAs(convertedBlob, fileName);
        })
        .catch((error) => {
          console.error("There was a problem with the fetch operation:", error);
        });

      toastifyMessage("Image has been downloaded", true);
    }
  }

  function saveImage(mimeType, quality, fileName) {
    preventFormFromDefaultAction();

    const imageBlob = dataURLtoBlob(mimeType, quality);

    if (imageBlob.size > maxImageBlobSize) {
      toastifyMessage("Image size cannot be more than 6 MB", false);
    } else {
      const formData = new FormData();
      formData.append("edited_image", imageBlob, fileName);

      fetch("/image_save/", {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken
        },
        body: formData
      }).then((response) => {
        console.log(response);
        if (response.ok) {
          console.log("Success");
        } else {
          console.error("Error");
        }
      });

      toastifyMessage("Image has been saved successfully", true);
      location.reload();
    }
  }
});