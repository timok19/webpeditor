Setup a virtual env for site-packages to keep all clean.

Steps to create:
1) Open a folder with the project
2) pip install virtualenv
3) Activate a bash script -> webpeditor_env\Scripts\activate

To deactivate:
1) Type in command promt -> deactivate

Add requirements.txt file:
1) Choose the folder, where you wanna save
2) pip freeze > requirements.txt

Install project:
1) In virtual_env -> pip install django
2) django-admin startproject name_of_project