from fabric.api import *
import os
import random
import string

# .Env
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def first_publish():
    """Publish to production.  THIS DESTROYS THE OLD BUILD."""
    heroku_app = '{0}-prod'.format(os.environ['HEROKU_PREFIX'])
    os.environ.setdefault('HEROKU_APP', heroku_app)
    local('heroku destroy {0} --confirm {0}'.format(heroku_app))
    local('heroku create {0} --buildpack https://github.com/heroku/heroku-buildpack-python --region eu'
          .format(heroku_app))
    local('heroku addons:create heroku-postgresql:hobby-dev --app {0}'.format(heroku_app))
    local('heroku pg:wait --app {0}'.format(heroku_app))
    local('heroku pg:backups:schedule --at 04:00 --app {0}'.format(heroku_app))
    # Already promoted as new local('heroku pg:promote DATABASE_URL --app bene-prod')
    # Leaving out and aws and reddis
    local("heroku config:set DJANGO_SETTINGS_MODULE=config.settings.production --app {}".format(heroku_app))
    local('heroku config:set PYTHONHASHSEED=random --app {}"'.format(heroku_app))
    local('heroku config:set DJANGO_ALLOWED_HOSTS="{}" --app {}'.format(os.environ['DJANGO_ALLOWED_HOSTS'], heroku_app))
    for config in ( 'DJANGO_SECRET_KEY', 'DJANGO_ADMIN_URL'
        ,'DJANGO_OPBEAT_ORGANIZATION_ID', 'DJANGO_OPBEAT_APP_ID', 'DJANGO_OPBEAT_SECRET_TOKEN'
        ,'DJANGO_AWS_ACCESS_KEY_ID', 'DJANGO_AWS_SECRET_ACCESS_KEY', 'DJANGO_AWS_STORAGE_BUCKET_NAME'
        ,'DJANGO_MAILGUN_API_KEY', 'DJANGO_SERVER_EMAIL', 'MAILGUN_SENDER_DOMAIN'
        ,'DJANGO_ACCOUNT_ALLOW_REGISTRATION', 'DJANGO_SENTRY_DSN'):
        local('heroku config:set {}={} --app {}'.format(config, os.environ[config], heroku_app))

    local('heroku git:remote -a {}'.format(heroku_app))
    local('git push heroku master')
    local('heroku run python manage.py migrate')
    local('heroku run python manage.py check --deploy') # make sure all ok
    local('heroku run python manage.py opbeat test')  # Test that opbeat is working
    su_name = os.environ['SUPERUSER_NAME']
    su_email = os.environ['SUPERUSER_EMAIL']
    su_password = os.environ['SUPERUSER_PASSWORD']
    cmd = ('heroku run "echo \'from django.contrib.auth import get_user_model; User = get_user_model(); '
        + f'User.objects.filter(email="""{su_email}""", is_superuser=True).delete(); '
        + f'User.objects.create_superuser("""{su_name}""", """{su_email}""", """{su_password}""")\' '
        + f' | python manage.py shell"' )
    local(cmd)
    # local('heroku open')  # opens the web site in a browser window.

