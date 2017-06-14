from fabric.api import *
import os
import random
import string

# .Env
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def first_publish():
    """Publish to production via rsync"""
    heroku_app = '{0}-prod'.format(os.environ['HEROKU_PREFIX'])
    local('heroku destroy {0} --confirm {0}'.format(heroku_app))
    local('heroku create {0} --buildpack https://github.com/heroku/heroku-buildpack-python --region eu'
          .format(heroku_app))
    local('heroku addons:create heroku-postgresql:hobby-dev --app {0}'.format(heroku_app))
    local('heroku pg:wait --app {0}'.format(heroku_app))
    local('heroku pg:backups:schedule --at 04:00 --app {0}'.format(heroku_app))
    # Already promoted as new local('heroku pg:promote DATABASE_URL --app bene-prod')
    # Leaving out mailgun and aws and reddis
    #local('heroku config:set DJANGO_ADMIN_URL="$(openssl rand -base64 32)" --app bene-prod')
    secret = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(20))
    print('Secret key = {}'.format(secret))
    local('heroku config:set DJANGO_SECRET_KEY="{}" --app {}'.format(secret, heroku_app))
    local("heroku config:set DJANGO_SETTINGS_MODULE=config.settings.production --app {}".format(heroku_app))
    local('heroku config:set PYTHONHASHSEED=random --app {}"'.format(heroku_app))
    local('heroku config:set DJANGO_ADMIN_URL=\^bene_admin/ --app {}"'.format(heroku_app))
    for config in ('DJANGO_ALLOWED_HOSTS'
        ,'DJANGO_OPBEAT_ORGANIZATION_ID', 'DJANGO_OPBEAT_APP_ID', 'DJANGO_OPBEAT_SECRET_TOKEN'
        ,'DJANGO_AWS_ACCESS_KEY_ID', 'DJANGO_AWS_SECRET_ACCESS_KEY', 'DJANGO_AWS_STORAGE_BUCKET_NAME'
        ,'DJANGO_MAILGUN_API_KEY', 'DJANGO_SERVER_EMAIL', 'MAILGUN_SENDER_DOMAIN'
        ,'DJANGO_ACCOUNT_ALLOW_REGISTRATION', 'DJANGO_SENTRY_DSN'):
        local('heroku config:set {}={} --app {}'.format(config, os.environ[config], heroku_app))

    local('heroku git:remote -a {}'.format(heroku_app))
    local('git push heroku master')

