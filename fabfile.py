from fabric.api import *
import json
import os
import re

# .Env
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def create_newbuild(env_prefix='test', branch='master'):
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
    local(f'git push heroku {branch}')
    local('heroku run python manage.py makemigrations')
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



def create_new_db(env_prefix='uat'):
    """Just creates a new database for this instance."""
    heroku_app = '{0}-{1}'.format(os.environ['HEROKU_PREFIX'], env_prefix)
    # Put the heroku app in maintenance move
    m = local('heroku addons:create heroku-postgresql:hobby-dev --app {0}'.format(heroku_app), capture=True)
    m1 = m.replace('\n',' ')  # Convert to a single string
    print(f'>>>{m1}<<<')
    found = re.search('Created\w*(.*)\w*as\w*(.*)\w* Use', m1)
    db_name = found.group(1)
    colour = found.group(2)
    print(f'DB colour = {colour}, {db_name}')
    local('heroku pg:wait')  # It takes some time for DB so wait for it
    return (colour, db_name)


def remove_unused_db(env_prefix='uat'):
    """List all databases in use for app, find the main one and remove all the others"""
    heroku_app = '{0}-{1}'.format(os.environ['HEROKU_PREFIX'], env_prefix)
    data = json.loads(local(f'heroku config --json --app {heroku_app}', capture=True))
    for k,v in data.items():
        if k.find('HEROKU_POSTGRESQL_') == 0:
            if v != data['DATABASE_URL']:
                local(f'heroku addons:destroy {k} --app {heroku_app} --confirm {heroku_app}')

def default_db_colour(app_name):
    """Return the default database colour of heroku application"""
    data = json.loads(local('heroku config --json --app {0}'.format(app_name), capture=True))
    result = ''
    for k,v in data.items():
        if k.find('HEROKU_POSTGRESQL_') == 0:
            if v == data['DATABASE_URL']:
                return k
    # if no colour found then try the long name in database_url
    # raise Exception(f'No color database names found for app {app_name} - create an extra one and it should be ok.')
    return data['DATABASE_URL']

def transfer_database_from_production(env_prefix='test', clean=True):
    heroku_app = '{0}-{1}'.format(os.environ['HEROKU_PREFIX'], env_prefix)
    heroku_app_prod = '{0}-prod'.format(os.environ['HEROKU_PREFIX'])
    # Put the heroku app in maintenance move
    try:
        local('heroku maintenance:on --app {} '.format(heroku_app) )
        colour, db_name = create_new_db(env_prefix)  # color is ?
        # Don't need to scale workers down as not using eg heroku ps:scale worker=0
        local(f'heroku pg:copy {heroku_app_prod}::DATABASE_URL {colour} --app {heroku_app} --confirm {heroku_app}')
        local(f'heroku pg:promote {colour}')
        if clean:
            remove_unused_db(env_prefix)
    finally:
        local('heroku maintenance:off --app {} '.format(heroku_app))


def kill_app(env_prefix, safety_on = True):
    if not (env_prefix == 'prod' and safety_on):  # Safety check - remove when you need to
        heroku_app = '{0}-{1}'.format(os.environ['HEROKU_PREFIX'], env_prefix)
        local('heroku destroy {0} --confirm {0}'.format(heroku_app))


def first_publish(env_prefix='prod'):
    """Publish to production.  THIS DESTROYS THE OLD BUILD."""
    heroku_app = '{0}-{1}'.format(os.environ['HEROKU_PREFIX'], env_prefix)
    os.environ.setdefault('HEROKU_APP', heroku_app)
    kill_app(env_prefix, safety_on=False)
    create_newbuild(env_prefix=env_prefix)
    # local('heroku open')  # opens the web site in a browser window.

#from build.new_db import create_staging, build_staging, update, kill_staging

def update_app(env_prefix='uat', branch='uat'):
    heroku_app = '{0}-{1}'.format(os.environ['HEROKU_PREFIX'], env_prefix)
    # Put the heroku app in maintenance move
    try:
        local('heroku maintenance:on --app {} '.format(heroku_app) )
        # connect git to the correct remote repository
        local('heroku git:remote -a {}'.format(heroku_app))
        # Need to push the branch in git to the master branch in the remote heroku repository
        local(f'git push heroku {branch}:master')
        # local(f'git push heroku {branch}')
        # makemigrations should be run locally and the results checked into git
        local('heroku run python manage.py migrate')
    finally:
        local('heroku maintenance:off --app {} '.format(heroku_app))


def build_staging(env_prefix='uat'):
    """THIS DESTROYS THE OLD BUILD. It builds a new environment with the uat branch."""
    heroku_app = '{0}-{1}'.format(os.environ['HEROKU_PREFIX'], env_prefix)
    os.environ.setdefault('HEROKU_APP', heroku_app)
    first_publish(env_prefix)
    transfer_database_from_production(env_prefix)
    # At this stage should have a copy of the master production system
    update_app(env_prefix)
    # local('heroku open')  # opens the web site in a browser window.


#if __name__ == "__main__":
    # staging = 'fac-test'
    # old_staging = staging
    # #create_staging(staging) # This builds the database and waits for it be ready.  It is is safe to run
    # #build_staging('BLUE', staging)
    # #update(staging)  #After simple fix which doesnt need DB rebuilding
    # kill_staging(old_staging)
    # #update('fac-prod')
