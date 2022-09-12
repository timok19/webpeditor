Setup a virtual env for site-packages to keep all clean.

Steps to create:
1) Open a folder with the project
2) $ pip install pipenv
3) In the same directory run command: $ pipenv shell

Install project:
1) In virtualenv (pipenv) -> pip install django
2) django-admin startproject name_of_project . 
->  (dot is for creating a project in the same directory)

Add requirements.txt file:
1) Choose the folder, where you wanna save
2) pip freeze > requirements.txt

Start server:
1) python manage.py runserver