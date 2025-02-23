![image](https://github.com/timok19/webpeditor/assets/87667470/f1f19b1c-243a-4b57-80f7-34084145cdfb)

## ℹ️ About
**WebP Editor** is a web-based image editing and conversion tool focused on the [**WebP**](https://developers.google.com/speed/webp) format.
It enables users to edit images with tools like cropping, scaling, and painting, as well as convert images to and from WebP and other major formats.
The app supports multiple file uploads and provides detailed image information.

---

## 🔀 Workflow
### Image Editor
1) The user is taken to the home page and uploads an image with an authorized format.
2) After uploading, the user will see an “Info” page with information about the image such as size, file name, aspect ratio, etc.
3) After clicking on the “Edit Image” button, the user will be redirected to the editor page where they can save, restore the original and download the image.

### Converter
1) User can upload multiple files (up to 10)
2) User selects the format of the image he wants to convert, and then click the convert button
3) After the conversion is complete, the user can see the difference between the original image and the converted image, and download all the converted images

---

## 🧩 Dependencies
### Backend
WebP Editor is build using the following libraries:
- ``Django`` - Popular python framework for building web applications.
- ``Pillow`` - Library for image manipulation.
- ``Cloudinary`` - Cloudinary cloud storage SDK.
- ``MongoDB`` - Document based database.

A complete list of dependencies can be found in the ``requirements.txt`` and ``requirements-dev.txt`` file.

### Frontend
Web application utilizes some popular libraries:
- ``ToastUI`` - Image editor with essential tools such as cropping, scaling, etc.
- ``Toastify`` - Better notification messages.
- ``TailwindCSS`` - A utility-first CSS framework.
- ``Flowbite`` - UI components.

A complete list of dependencies can be found in the ``package.json`` file.

The app is hosted using the [Fly.io](https://fly.io/) service at this [**link**](https://webpeditor.fly.dev/).

---

## ▶️ Project setup

**Steps to run project:**

**1. Clone repo:**
- `$ git clone https://github.com/timok19/webpeditor.git`

**2. Install necessary dependencies:**
- Backend: `$ uv venv && source .venv/bin/activate && uv sync`
- Frontend: `$ pnpm install`

**3. Start server:**
- `$ python manage.py runserver`

**4. Run TailwindCSS watcher:**
- `$ pnpm run update-css`

**5. DONE 🚀**

---

For any questions, concerns or issues contact me on [LinkedIn](https://www.linkedin.com/in/temirkhan-amanzhanov-5b182b1b6/?locale=en_US) or [Email](mailto:webpeditor@gmail.com)
