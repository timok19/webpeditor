document.addEventListener("DOMContentLoaded", function () {
  const ImageEditor = tui.ImageEditor;
  const container = document.querySelector("#tui-image-editor");

  const csrfTokenElement = document.getElementById("csrfToken");
  const csrfToken = csrfTokenElement ? JSON.parse(csrfTokenElement.textContent) : null;

  const imageUrlElement = document.getElementById("imageUrl");
  let imageUrl = imageUrlElement ? JSON.parse(imageUrlElement.textContent) : null;

  const imageContentTypeElement = document.getElementById("imageContentType");
  const imageContentType = imageContentTypeElement ? JSON.parse(imageContentTypeElement.textContent) : null;

  const imageNameElement = document.getElementById("imageName");
  let imageName = imageNameElement ? JSON.parse(imageNameElement.textContent) : null;

  const maxImageBlobSize = 6291456;

  const editor = new ImageEditor(container, {
    includeUI: {
      loadImage: {
        path: imageUrl,
        name: imageName,
      },
      theme: {
        "common.backgroundImage": "none",
        "common.backgroundColor": "transparent",
      },
      menu: ["resize", "crop", "flip", "rotate", "draw", "shape", "icon", "text", "mask", "filter"],
      uiSize: {
        width: window.innerHeight < 768 ? "52rem" : "62rem",
        height: window.innerHeight < 768 ? "36rem" : "42rem",
      },
      menuBarPosition: "left",
    },
    cssMaxWidth: window.innerWidth < 768 ? "700" : "750",
    cssMaxHeight: window.innerHeight < 768 ? "500" : "550",
    usageStatistics: false,
    selectionStyle: {
      cornerSize: 20,
      rotatingPointOffset: 70,
    },
  });

  // Delete Upload button
  document.querySelector(".tui-image-editor-header-buttons div").remove();

  // Set height of svg object with icons to 0
  document.querySelector("svg[display='none']").style.height = 0

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
  svgDownloadPath.setAttribute(
    "d",
    "M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 " +
      "1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m.75 12l3 3m0 0l3-3m-3 3v-6m-1.5-9H5.625c-.621 " +
      "0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
  );
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
  downloadButton.setAttribute("data-tooltip-target", "tooltip-download");
  downloadButton.setAttribute("data-tooltip-placement", "bottom");
  downloadButton.setAttribute("type", "button");

  const tooltipDownload = addToolTip("Download image", "tooltip-download");
  downloadButton.addEventListener("mouseenter", () => {
    tooltipDownload.classList.remove("invisible");
  });
  downloadButton.addEventListener("mouseleave", () => {
    tooltipDownload.classList.add("invisible");
  });

  downloadButton.className =
    "relative inline-flex items-center justify-center p-0.5 mb-2 mr-2 ml-2 mt-2 overflow-hidden " +
    "text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-pink-500 to-orange-400 " +
    "group-hover:from-pink-500 group-hover:to-orange-400 hover:text-white dark:text-white focus:ring-4 " +
    "focus:outline-none focus:ring-pink-200 dark:focus:ring-pink-800 text-center";
  downloadButton.appendChild(addIconIntoButton(svgDownloadIcon));
  document.body.appendChild(tooltipDownload);

  // Save button
  let saveButton = document.createElement("button");
  saveButton.addEventListener("click", () => saveImage(imageContentType, 1, imageName));
  saveButton.id = "tuiSaveButton";
  saveButton.setAttribute("data-tooltip-target", "tooltip-save");
  saveButton.setAttribute("data-tooltip-placement", "bottom");
  saveButton.setAttribute("type", "button");

  const tooltipSave = addToolTip("Save image", "tooltip-save");
  saveButton.addEventListener("mouseenter", () => {
    tooltipSave.classList.remove("invisible");
  });
  saveButton.addEventListener("mouseleave", () => {
    tooltipSave.classList.add("invisible");
  });

  saveButton.className =
    "relative inline-flex items-center justify-center p-0.5 mb-2 mr-2 ml-2 mt-2 overflow-hidden " +
    "text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-pink-500 to-orange-400 " +
    "group-hover:from-pink-500 group-hover:to-orange-400 hover:text-white dark:text-white focus:ring-4 " +
    "focus:outline-none focus:ring-pink-200 dark:focus:ring-pink-800 text-center";
  saveButton.appendChild(addIconIntoButton(svgSaveIcon));
  document.body.appendChild(tooltipSave);

  // Original image button
  let originalImageButton = document.createElement("button");
  originalImageButton.addEventListener("click", () => getOriginalImage());
  originalImageButton.id = "tuiOriginalImageButton";
  originalImageButton.setAttribute("data-tooltip-target", "tooltip-restore-original-image");
  originalImageButton.setAttribute("data-tooltip-placement", "bottom");
  originalImageButton.setAttribute("type", "button");

  const tooltipRestore = addToolTip("Restore original image", "tooltip-restore-original-image");
  originalImageButton.addEventListener("mouseenter", () => {
    tooltipRestore.classList.remove("invisible");
  });
  originalImageButton.addEventListener("mouseleave", () => {
    tooltipRestore.classList.add("invisible");
  });

  originalImageButton.className =
    "relative inline-flex items-center justify-center p-0.5 mb-2 mr-2 ml-2 mt-2 overflow-hidden " +
    "text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-pink-500 to-orange-400 " +
    "group-hover:from-pink-500 group-hover:to-orange-400 hover:text-white dark:text-white focus:ring-4 " +
    "focus:outline-none focus:ring-pink-200 dark:focus:ring-pink-800 text-center";
  originalImageButton.appendChild(addIconIntoButton(svgOriginalImageIcon));
  document.body.appendChild(tooltipRestore);

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
  menuFilter.style.overflowY = "overlay";

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
  svgImageInfoPath.setAttribute(
    "d",
    "M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z"
  );
  svgImageInfoIcon.appendChild(svgImageInfoPath);

  // Image info popover button
  let imageInfoButton = document.createElement("button");
  imageInfoButton.setAttribute("data-popover-target", "popover-description");
  imageInfoButton.setAttribute("data-popover-placement", "left");
  imageInfoButton.setAttribute("type", "button");
  imageInfoButton.style.marginBottom = "2rem";
  imageInfoButton.appendChild(svgImageInfoIcon);

  let menu = document.querySelector(".tui-image-editor-menu");
  menu.insertBefore(imageInfoButton, menu.firstElementChild);

  const imageEditorContainer = document.querySelector("#tui-image-editor");
  imageEditorContainer.style.borderRadius = "1rem";
  imageEditorContainer.classList.add("shadow");
  imageEditorContainer.classList.add("border");
  imageEditorContainer.classList.add("border-gray-200");
  imageEditorContainer.classList.add("dark:bg-gray-800");
  imageEditorContainer.classList.add("dark:border-gray-700");

  applyDarkModeOnEditorContainer(imageEditorContainer);

  const themeButton = document.getElementById("theme-toggle");
  themeButton.addEventListener("click", () => applyDarkModeOnEditorContainer(imageEditorContainer));

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

  const imageEditorSizeWrap = document.querySelector(".tui-image-editor-size-wrap");
  imageEditorSizeWrap.style.display = "flex";
  imageEditorSizeWrap.style.justifyContent = "center";

  const imageEditorAlignWrap = document.querySelector(".tui-image-editor-align-wrap");
  imageEditorAlignWrap.style.display = "flex";
  imageEditorAlignWrap.style.alignItems = "center";

  // Span with text and icon
  function addIconIntoButton(icon) {
    const span = document.createElement("span");
    span.className =
      "relative px-2 py-2 transition-all ease-in duration-75 bg-white dark:bg-gray-900 " +
      "rounded-md group-hover:bg-opacity-0 text-center inline-flex items-center";
    span.appendChild(icon);

    return span;
  }

  // Add tooltip to button
  function addToolTip(text, dataTooltipTargetId) {
    let divTooltip = document.createElement("div");
    divTooltip.id = `${dataTooltipTargetId}`;
    divTooltip.setAttribute("role", "tooltip");
    divTooltip.className =
      "absolute tooltip z-10 invisible px-3 py-2 font-light transition-opacity " +
      "duration-300 bg-gray-900 rounded-lg shadow-sm opacity-0 dark:bg-gray-700";

    let divTooltipText = document.createElement("div");
    divTooltipText.className = "text-sm text-white";
    divTooltipText.style.padding = "0.2rem";
    divTooltipText.textContent = text;
    divTooltip.appendChild(divTooltipText);

    let divTooltipArrow = document.createElement("div");
    divTooltipArrow.className = "tooltip-arrow";
    divTooltipArrow.setAttribute("data-popper-arrow", "");

    divTooltip.appendChild(divTooltipArrow);
    return divTooltip;
  }

  function applyDarkModeOnEditorContainer(element) {
    let colorTheme = localStorage.getItem("color-theme") === "dark" ? "dark" : "light";

    if (colorTheme === "dark") {
      element.style.background = "#1F2937";
    } else {
      element.style.background = "rgb(255 255 255 / var(--tw-bg-opacity))";
    }
  }

  function editCanvasSize(queryClass) {
    const canvas = document.querySelector(queryClass);
    canvas.style.position = "absolute";
    canvas.style.width = "400px";
    canvas.style.height = "400px";
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
      quality: quality,
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

      fetch("/api/image_download/", {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
        },
        body: formData,
      })
        .then((response) => {
          if (!response.ok) {
            const errorMessage = "Error: image cannot be saved";
            toastifyMessage(errorMessage, false);
            throw new Error(errorMessage);
          }
          return response.blob();
        })
        .then((convertedBlob) => {
          saveAs(convertedBlob, fileName);
          toastifyMessage("Image has been downloaded", true);
        })
        .catch((error) => {
          console.error("There was a problem with the fetch operation:", error);
        });
    }
  }

  function saveImage(mimeType, quality, fileName) {
    preventFormFromDefaultAction();

    const imageBlob = dataURLtoBlob(mimeType, quality);

    const formData = new FormData();
    formData.append("edited_image", imageBlob, fileName);

    fetch("/api/image_save/", {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfToken,
      },
      body: formData,
    })
      .then((response) => {
        if (!response.ok) {
          toastifyMessage("Failed to save image", false);
          throw new Error("Network response was not ok");
        }

        if (imageBlob.size > maxImageBlobSize) {
          const errorMessage = "Image size should not exceed 6 MB";
          toastifyMessage(errorMessage, false);

          throw new Error(errorMessage);
        } else {
          toastifyMessage("Image has been saved successfully", true);
        }

        location.reload();
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

  function getOriginalImage() {
    preventFormFromDefaultAction();

    fetch("/api/image_get_original/", {
      method: "GET",
      headers: {
        "X-CSRFToken": csrfToken,
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch the original image");
        }
        const imageName = response.headers.get("X-Image-Name");
        return response.blob().then((imageBlob) => ({ imageBlob, imageName }));
      })
      .then(({ imageBlob, imageName }) => {
        const imageFile = new File([imageBlob], imageName, {
          type: imageBlob.type,
        });

        // Load the new image into the editor
        editor.loadImageFromFile(imageFile, imageName).then((result) => {
          console.log("Image loaded successfully:", result);
        });

        toastifyMessage("Original image is loaded", true);
      })
      .catch((error) => {
        console.error("Error:", error);
        toastifyMessage("Failed to open the original image", false);
      });
  }
});