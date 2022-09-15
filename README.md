## Setup a virtual env for site-packages to keep all clean
---
__Steps to create:__
1. Open a folder with the project
2. `$ pip install pipenv`
3. In the same directory run command: `$ pipenv shell` -> to deactivate already opened virtualenv -> `$ deactivate`.
-> to deactivate currently opened virtualenv -> `$ exit`

__Install project:__
1. In *virtualenv* *(pipenv)* -> `$ pip install django`
2. `$ django-admin startproject name_of_project .` -> (`.` is for creating a project in the same directory)

__Add requirements.txt file:__
1. Choose the folder, where you wanna save
2. `$ pip freeze > requirements.txt`

__Start server:__
1. `$ python manage.py runserver`