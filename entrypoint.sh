@echo off

:: Run makemigrations
python manage.py makemigrations

:: Run migrate
python manage.py migrate

:: Run runserver
python manage.py runserver 0.0.0.0:8000