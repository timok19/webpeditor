## Project setup

---

**Steps to create:**

1. Open a folder with the project
2. `$ pip install pipenv`
3. In the same directory run command: `$ pipenv shell` -> to deactivate already opened virtualenv -> `$ deactivate`.
   -> to deactivate currently opened virtualenv -> `$ exit`

**1. Install project:**

1. In _virtualenv_ _(pipenv)_ -> `$ pip install django`
2. `$ django-admin startproject name_of_project .` -> (`.` is for creating a project in the same directory)

**2. Add requirements.txt file:**

1. Choose the folder, where you wanna save
2. `$ pip freeze > requirements.txt`

**3. Start server:**

1. `$ python manage.py runserver`

**4. Install Tailwind CSS:**

1. `$ npm install -D tailwindcss`
2. `$ npx tailwindcss init` -> add specific configs

**5. Run the following command to watch for changes and compile the Tailwind CSS code:**

1. `$ npx tailwindcss -i ./static/src/input.css -o ./static/src/output.css --watch`

**6. Install Flowbite**

1. `$ npm i flowbite`
