REM See readme.mkd, this batch file is for setting up a local version.
REM You need a local version for database migrations.
set DJANGO_READ_DOT_ENV_FILE=True
set DJANGO_SETTINGS_MODULE=config.settings.local
python manage.py runserver
