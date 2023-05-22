![image](https://github.com/timok19/webpeditor/assets/87667470/f1f19b1c-243a-4b57-80f7-34084145cdfb)

## ℹ️ About WebP Editor
This Django application uses JS libraries (ToastUI image editor for editing images with essential tools such as cropping, scaling, etc., and Toastify for toast messages). 

On the back-end, one external service CoudinaryAPI has been used for storing/deleting images for users on external FileStorage. MongoDB was chosen as a primary database where users' data is stored. 

Image converter was created with the Python library Pillow. It can be changed because of format support issues.

How does it works:
1) User lands on the Home page and upload image with allowed format.
2) After upload user will see an Info page with image information such as size, file name, aspect ratio etc.
3) After clicking on "Edit image" user will be redirected to the Editor page, where he can save, restore original and download image.

On Converter page:
1) User is able to upload multiple files (up to 15)
2) User will choose an image format what he wants to convert and then click on convert
3) After conversion finished user is able to see difference between original and converted image and download all converted images

Currently, this web application is deployed with service Fly.io on this link: https://webpeditor.fly.dev/. Please fill free to try it out. 

---

## ▶️ Project setup

**Steps to run project:**

**1. Clone repo:**

1. Clone repo from https://github.com/timok19/webpeditor.git

**2. Install necessary dependencies:**

1. `$ pip install pipenv && pipenv install --dev && pipenv update`
2. `$ npm install`

**3. Start server:**

1. `$ python manage.py runserver`

**4. Run TailwindCSS watcher:**

1. `$ npm run update-css`

**5. DONE 🚀**

For any questions, problems, or issues, contact me on [LinkedIn](https://www.linkedin.com/in/temirkhan-amanzhanov-5b182b1b6/?locale=en_US).
