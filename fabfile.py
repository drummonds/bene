from fabric.api import *
import os
import random
import string

# .Env
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def create_staging(env_prefix='test'):
    """This builds the database and waits for it be ready.  It is is safe to run and won't
    destroy any existing infrastructure."""
    # subprocess.call('heroku create --app {} --region eu'.format(staging), shell=True)
    heroku_app = '{0}-{1}'.format(os.environ['HEROKU_PREFIX'], env_prefix)
    #local('heroku create --app {} --region eu'.format(heroku_app))  # Old style
    local('heroku create {0} --buildpack https://github.com/heroku/heroku-buildpack-python --region eu'
          .format(heroku_app))
    # This is where we create the database.  The type of database can range from hobby-dev for small
    # free access to standard for production quality docs
    local('heroku addons:create heroku-postgresql:hobby-dev --app {0}'.format(heroku_app))
    local('heroku pg:wait --app {0}'.format(heroku_app))  # It takes some time for DB so wait for it
    local('heroku pg:backups:schedule --at 04:00 --app {0}'.format(heroku_app))
    # Already promoted as new local('heroku pg:promote DATABASE_URL --app bene-prod')
    # Leaving out and aws and reddis
    local("heroku config:set DJANGO_SETTINGS_MODULE=config.settings.production --app {}".format(heroku_app))
    local('heroku config:set PYTHONHASHSEED=random --app {}"'.format(heroku_app))
    local('heroku config:set DJANGO_ALLOWED_HOSTS="{1}.herokuapp.com" --app {1}'.format(os.environ['DJANGO_ALLOWED_HOSTS'], heroku_app))
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
    # Old code
    # subprocess.call('git remote add {0} git@heroku.com:{0}.git'.format(staging), shell=True)
    # a=subprocess.check_output('heroku addons:add heroku-postgresql:standard-0 --app {} '.format(staging),
    #                           shell=True )
    # print("DB build result = |{}|".format(a))
    # subprocess.call('heroku pg --app {}'.format(staging), shell=True)
    #
    #  # Get backup from production to test
    #  ## First make sure they have the backup addon
    # subprocess.call('heroku addons:add pgbackups --app {} '.format(staging), shell=True )
    #
    # subprocess.call('heroku pg:wait --app {} '.format(staging), shell=True )

def kill_staging(env_prefix, safety_on = True):
    if not (env_prefix == 'prod' and safety_on):  # Safety check - remove when you need to
        heroku_app = '{0}-{1}'.format(os.environ['HEROKU_PREFIX'], env_prefix)
        local('heroku destroy {0} --confirm {0}'.format(heroku_app))


def first_publish(env_prefix='prod'):
    """Publish to production.  THIS DESTROYS THE OLD BUILD."""
    heroku_app = '{0}-{1}'.format(os.environ['HEROKU_PREFIX'], env_prefix)
    os.environ.setdefault('HEROKU_APP', heroku_app)
    kill_staging(env_prefix, safety_on=False)
    create_staging(env_prefix=env_prefix)
    # local('heroku open')  # opens the web site in a browser window.

#from build.new_db import create_staging, build_staging, update, kill_staging


#if __name__ == "__main__":
    # staging = 'fac-test'
    # old_staging = staging
    # #create_staging(staging) # This builds the database and waits for it be ready.  It is is safe to run
    # #build_staging('BLUE', staging)
    # #update(staging)  #After simple fix which doesnt need DB rebuilding
    # kill_staging(old_staging)
    # #update('fac-prod')
