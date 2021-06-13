# bene
A reporting sytem and interface to Xero

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg)](https://github.com/pydanny/cookiecutter-django/)

[![Travis CI](https://travis-ci.org/drummonds/bene.svg?branch=master)](https://travis-ci.org/drummonds/bene)

License  
GPLv3

## Settings


Moved to
[settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

## Basic Commands

### Setting Up Your Users

-   To create a **normal user account**, just go to Sign Up and fill out
    the form. Once you submit it, you'll see a "Verify Your E-mail
    Address" page. Go to your console to see a simulated email
    verification message. Copy the link into your browser. Now the
    user's email should be verified and ready to go.
-   To create an **superuser account**, use this command:

        $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and
your superuser logged in on Firefox (or similar), so that you can see
how the site behaves for both kinds of users.

## Test coverage

To run the tests, check your test coverage, and generate an HTML
coverage report:

    $ coverage run manage.py test
    $ coverage html
    $ open htmlcov/index.html

### Running tests with py.test

    $ py.test

## Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS
compilation](http://cookiecutter-django.readthedocs.io/en/latest/live-reloading-and-sass-compilation.html).

Email Server
------------

In development, it is often nice to be able to see emails that are being
sent from your application. If you choose to use
[MailHog](https://github.com/mailhog/MailHog) when generating the
project a local SMTP server with a web interface will be available.

To start the service, make sure you have nodejs installed, and then type
the following:

    $ npm install
    $ grunt serve

(After the first run you only need to type `grunt serve`) This will
start an email server that listens on `127.0.0.1:1025` in addition to
starting your Django project and a watch task for live reload.

To view messages that are sent by your application, open your browser
and go to `http://127.0.0.1:8025`

The email server will exit when you exit the Grunt task on the CLI with
Ctrl+C.

## Sentry

Sentry is an error logging aggregator service. You can sign up for a
free account at <https://sentry.io/signup/?code=cookiecutter> or
download and host it yourself. The system is setup with reasonable
defaults, including 404 logging and integration with the WSGI
application.

You must set the DSN url in production.

## Deployment

Requirements:

The following details how to deploy this application.

## Heroku


See detailed [cookiecutter-django Heroku
documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-on-heroku.html).


## Local deployment

Having set up the file you need to store your local settings in a .env file.  Then you will need 
the following settings (this is automated for Windows in the file `a.bat`).

    set DJANGO_READ_DOT_ENV_FILE=True
    set DJANGO_SETTINGS_MODULE=config.settings.local
    set DJANGO_AWS_STORAGE_BUCKET_NAME=bene-test
    python manage.py runserver

then `python manage.py makemigrations` will work fine.

The easiest way to configure the local database if you have a working version on heroku
is to backup the heroku data to a local file and the restore to the local data from this.
(making a copy of your previous database before you start. Restore all data and confirm email
by updating DB)

## Build chain

To build the project you need to do the following:

1. Download from github the project
2. Build the bene virtual environment with python 3.6+
   1. install homebrew
   2. `brew install pyenv`
   3. `pyenv doctor` check ok
   4. `pyenv install 3.9.5`  or I had to use `CONFIGURE_OPTS="--with-openssl=$(brew --prefix openssl)" pyenv install 3.9.5pyu` latest desired version supported by heroku
   5. `pyenv versions` check it has installed correctly
   ```
   poetry shell
   fab --list
   ```
   To check that all installed ok.
3. Copy the .env or fill it in from the example  need to edit heroku_prefix and add herok api
4. Install [Heroku CLI][] (was part of toolbelt)
    1. Download and install software
    2. logout of command window if logged in and log backin so that
    new path is used
    1. set up app again eg workon bene and cd
    2. heroku login to store user id
 1. Test build with `fab create_newuild`
     

### Building the environment with poetry
You can set up the local environment with poetry.

- install poetry
- The pyproject.toml file has the development build required
- 

[Heroku CLI]: https://devcenter.heroku.com/articles/heroku-cli#download-and-install

