document.addEventListener("DOMContentLoaded", function() {
  const ImageEditor = tui.ImageEditor;
  const container = document.querySelector("#tui-image-editor");

  const imageUrl = JSON.parse(document.getElementById("imageUrlId").textContent);
  const imageName = "ImageResult";

  const options = {
    includeUI: {
      loadImage: {
        path: imageUrl,
        name: imageName
      },
      theme: {
        "common.backgroundImage": "none",
        "common.backgroundColor": "#111827"
      },
      menu: ["crop", "flip", "rotate", "draw", "shape", "icon", "text", "mask", "filter"],
      uiSize: {
        width: "100%",
        height: "82vh"
      },
      menuBarPosition: "bottom"

    },
    cssMaxWidth: 700,
    cssMaxHeight: 500,
    usageStatistics: false
  };

  const editor = new ImageEditor(container, options);

  // Delete Upload button
  document.querySelector(".tui-image-editor-header-buttons div").remove();

  // Save Icon svg (Save button)
  const svgSaveIcon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svgSaveIcon.setAttribute("fill", "none");
  svgSaveIcon.setAttribute("stroke-width", "1.5");
  svgSaveIcon.setAttribute("viewBox", "0 0 24 24");
  svgSaveIcon.setAttribute("stroke", "currentColor");
  svgSaveIcon.setAttribute("aria-hidden", "true");
  svgSaveIcon.setAttribute("class", "w-6 h-6");

  // Path icon (Save button)
  const svgPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
  svgPath.setAttribute("stroke-linecap", "round");
  svgPath.setAttribute("stroke-linejoin", "round");
  svgPath.setAttribute("fill-rule", "evenodd");
  svgPath.setAttribute("clip-rule", "evenodd");
  svgPath.setAttribute("d", "M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 " +
    "1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m.75 12l3 3m0 0l3-3m-3 3v-6m-1.5-9H5.625c-.621 " +
    "0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z");
  svgSaveIcon.appendChild(svgPath);

  // Span with text and icon (Save button)
  const spanText = document.createElement("span");
  spanText.className = "relative px-2 py-2 transition-all ease-in duration-75 bg-white dark:bg-gray-900 " +
    "rounded-md group-hover:bg-opacity-0 text-center inline-flex items-center";
  spanText.textContent = "Save image" + String.fromCharCode(160);
  spanText.appendChild(svgSaveIcon);

  // Save button
  const saveButton = document.querySelector(".tui-image-editor-header-buttons button");
  saveButton.removeAttribute("style");
  saveButton.id = "tuiSaveButton";
  saveButton.className = "relative inline-flex items-center justify-center p-0.5 mb-2 mr-2 ml-2 mt-2 overflow-hidden " +
    "text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-pink-500 to-orange-400 " +
    "group-hover:from-pink-500 group-hover:to-orange-400 hover:text-white dark:text-white focus:ring-4 " +
    "focus:outline-none focus:ring-pink-200 dark:focus:ring-pink-800 text-center";
  saveButton.textContent = "";
  saveButton.appendChild(spanText);

  saveButton.addEventListener('click', saveImageHandler);

  // Div with Save button
  const newDiv = document.createElement("div");
  saveButton.parentNode.insertBefore(newDiv, saveButton);
  newDiv.appendChild(saveButton);
  newDiv.style.display = "flex";
  newDiv.style.flexDirection = "row-reverse";

  const subItemMaskChoice = document.querySelector(".tui-image-editor-menu-mask ul.tui-image-editor-submenu-item");
  subItemMaskChoice.style.marginTop = "0.5rem";

  // Deleting logo
  document.querySelector(".tui-image-editor-header-logo").remove();

  // Lower menu
  document.querySelector(".tui-image-editor-controls").style.backgroundColor = "#111827";

  // Top menu buttons
  const topButtons = document.querySelector(".tui-image-editor-header div.tui-image-editor-header-buttons");
  topButtons.removeAttribute("class");

  // Top menu
  const topMenu = document.querySelector("ul.tui-image-editor-help-menu");
  topMenu.style.marginTop = "0.1rem";
  topMenu.style.borderRadius = "0.4rem";

  function saveImageHandler() {
    if (isSaving) {
      return;
    }

    let isSaving = true;
    // Generate the data URL of the edited image
    const dataURL = editor.toDataURL();

    // Convert base64 data URL to a Blob
    const data = atob(dataURL.split(",")[1]);
    const arrayBuffer = new ArrayBuffer(data.length);
    const view = new Uint8Array(arrayBuffer);
    for (let i = 0; i < data.length; i++) {
      view[i] = data.charCodeAt(i) & 0xff;
    }
    const blob = new Blob([arrayBuffer], { type: "image/png" });

    // Use the FileSaver library's saveAs function to download the image
    saveAs(blob, "edited-image.png");
    isSaving = false;
  }
});