import datetime as dt
from fabric.api import *
import json
import os
import re
import time

# .Env
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

##################################################
# Local utilities
##################################################


def remove_unused_db(env_prefix="uat"):
    """List all databases in use for app, find the main one and remove all the others"""
    heroku_app = "{0}-{1}".format(os.environ["HEROKU_PREFIX"], env_prefix)
    data = json.loads(local(f"heroku config --json --app {heroku_app}", capture=True))
    for k, v in data.items():
        if k.find("HEROKU_POSTGRESQL_") == 0:
            if v != data["DATABASE_URL"]:
                local(
                    f"heroku addons:destroy {k} --app {heroku_app} --confirm {heroku_app}"
                )


def default_db_colour(app_name):
    """Return the default database colour of heroku application"""
    data = json.loads(
        local("heroku config --json --app {0}".format(app_name), capture=True)
    )
    result = ""
    for k, v in data.items():
        if k.find("HEROKU_POSTGRESQL_") == 0:
            if v == data["DATABASE_URL"]:
                return k
    # if no colour found then try the long name in database_url
    # raise Exception(f'No color database names found for app {app_name} - create an extra one and it should be ok.')
    return data["DATABASE_URL"]


def set_environment_variables(env_prefix):
    if env_prefix == "test":  # TODO move to settings
        settings = "develop"
    else:
        settings = "production"
    heroku_app = "{0}-{1}".format(os.environ["HEROKU_PREFIX"], env_prefix)
    local(
        f"heroku config:set DJANGO_SETTINGS_MODULE=config.settings.{settings} --app {heroku_app}"
    )
    # default from 3.4 local('heroku config:set PYTHONHASHSEED=random --app {}'.format(heroku_app))
    local(
        'heroku config:set DJANGO_ALLOWED_HOSTS="{1}.herokuapp.com" --app {1}'.format(
            os.environ["DJANGO_ALLOWED_HOSTS"], heroku_app
        )
    )
    for config in (
        "DJANGO_SECRET_KEY",
        "DJANGO_ADMIN_URL",
        "DJANGO_AWS_ACCESS_KEY_ID",
        "DJANGO_AWS_SECRET_ACCESS_KEY",
        "DJANGO_AWS_STORAGE_BUCKET_NAME",
        "DJANGO_MAILGUN_API_KEY",
        "DJANGO_SERVER_EMAIL",
        "MAILGUN_SENDER_DOMAIN",
        "DJANGO_ACCOUNT_ALLOW_REGISTRATION",
        "DJANGO_SENTRY_DSN",
        "XERO_CONSUMER_SECRET",
        "XERO_CONSUMER_KEY",
    ):
        local(
            "heroku config:set {}={} --app {}".format(
                config, os.environ[config], heroku_app
            )
        )


##################################################
# Tasks
##################################################


@task
def create_newbuild(env_prefix="test", branch="master"):
    """This builds the database and waits for it be ready.  It is is safe to run and won't
    destroy any existing infrastructure."""
    # subprocess.call('heroku create --app {} --region eu'.format(staging), shell=True)
    heroku_app = "{0}-{1}".format(os.environ["HEROKU_PREFIX"], env_prefix)
    # local('heroku create --app {} --region eu'.format(heroku_app))  # Old style
    local(
        "heroku create {0} --buildpack https://github.com/heroku/heroku-buildpack-python --region eu".format(
            heroku_app
        )
    )
    # This is where we create the database.  The type of database can range from hobby-dev for small
    # free access to standard for production quality docs
    local(
        "heroku addons:create heroku-postgresql:hobby-basic --app {0}".format(
            heroku_app
        )
    )
    local(f"heroku addons:create cloudamqp:lemur --app {heroku_app}")
    local(f"heroku addons:create papertrail:choklad --app {heroku_app}")
    # Add guvscale processing to allow celery queue to be at zero
    # guvscale seems not to work in beta
    # local(f'heroku addons:create guvscale --app {heroku_app}')
    try:
        local(
            f"heroku plugins:install heroku-cli-oauth"
        )  # installed in local toolbelt not on app
    except:
        print("Probably already installed")
    # Now need to create a token and add to guvscale
    # Does'nt work
    # data = json.loads(local(
    #    f'heroku authorizations:create --json --description "GuvScale" -s write,read-protected --app {heroku_app}',
    #    capture=True))
    # print(f'Data for guvscale = :{data}')
    # Load guvscale cli tool (may already be installed)
    try:
        local(
            f"heroku plugins:install heroku-guvscale"
        )  # installed in local toolbelt not on app
    except:
        print("Probably already installed")
    # start of configuring guvscale to autoscale
    # local(f'heroku guvscale:getconfig --app {heroku_app}')
    # set database backup schedule
    local(
        "heroku pg:wait --app {0}".format(heroku_app)
    )  # It takes some time for DB so wait for it
    local("heroku pg:backups:schedule --at 04:00 --app {0}".format(heroku_app))
    # Already promoted as new local('heroku pg:promote DATABASE_URL --app bene-prod')
    # Leaving out and aws and reddis
    raw_update_app(env_prefix, branch=branch)
    local("heroku run python manage.py check --deploy")  # make sure all ok
    su_name = os.environ["SUPERUSER_NAME"]
    su_email = os.environ["SUPERUSER_EMAIL"]
    su_password = os.environ["SUPERUSER_PASSWORD"]
    cmd = (
        "heroku run \"echo 'from django.contrib.auth import get_user_model; User = get_user_model(); "
        + f'User.objects.filter(email="""{su_email}""", is_superuser=True).delete(); '
        + f'User.objects.create_superuser("""{su_name}""", """{su_email}""", """{su_password}""")\' '
        + f' | python manage.py shell"'
    )
    local(cmd)


def raw_update_app(env_prefix="uat", branch="master"):
    """Update of app to latest version"""
    heroku_app = "{0}-{1}".format(os.environ["HEROKU_PREFIX"], env_prefix)
    # Put the heroku app in maintenance move
    set_environment_variables(env_prefix)  # In case anything has changed
    # connect git to the correct remote repository
    local("heroku git:remote -a {}".format(heroku_app))
    # Need to push the branch in git to the master branch in the remote heroku repository
    local(f"git push heroku {branch}:master")
    # Don't need to scale workers down as not using eg heroku ps:scale worker=0
    # Will add guvscale to spin workers up and down from 0
    local(f"heroku ps:scale worker=1 -a {heroku_app}")
    # Have used performance web=standard-1x and worker=standard-2x but adjusted app to used less memory
    # local(f'heroku ps:resize web=standard-1x -a {heroku_app}')  # Resize web to be compatible with performance workers
    # local(f'heroku ps:resize worker=standard-2x -a {heroku_app}')  # Resize workers
    # makemigrations should be run locally and the results checked into git
    local(
        "heroku run \"yes 'yes' | python manage.py migrate\""
    )  # Force deletion of stale content types


@task
def update_app(env_prefix="uat", branch="master"):
    """Protected update with maintenance on"""
    heroku_app = "{0}-{1}".format(os.environ["HEROKU_PREFIX"], env_prefix)
    # Put the heroku app in maintenance move
    try:
        local("heroku maintenance:on --app {} ".format(heroku_app))
        raw_update_app(env_prefix, branch)
    finally:
        local("heroku maintenance:off --app {} ".format(heroku_app))


@task
def create_new_db(env_prefix="uat"):
    """Just creates a new database for this instance."""
    heroku_app = "{0}-{1}".format(os.environ["HEROKU_PREFIX"], env_prefix)
    # Put the heroku app in maintenance move
    m = local(
        "heroku addons:create heroku-postgresql:hobby-basic --app {0}".format(
            heroku_app
        ),
        capture=True,
    )
    m1 = m.replace("\n", " ")  # Convert to a single string
    print(f">>>{m1}<<<")
    found = re.search("Created\w*(.*)\w*as\w*(.*)\w* Use", m1)
    db_name = found.group(1)
    colour = found.group(2)
    print(f"DB colour = {colour}, {db_name}")
    local("heroku pg:wait")  # It takes some time for DB so wait for it
    return (colour, db_name)


@task
def transfer_database_from_production(env_prefix="test", clean=True):
    """This is usally used for making a copy of the production database for a UAT staging
    or test environment.  It can also be used to upgrade the production environment from one
    database plan to the next."""
    heroku_app = "{0}-{1}".format(os.environ["HEROKU_PREFIX"], env_prefix)
    heroku_app_prod = "{0}-prod".format(os.environ["HEROKU_PREFIX"])
    # Put the heroku app in maintenance move
    try:
        local("heroku maintenance:on --app {} ".format(heroku_app))
        colour, db_name = create_new_db(env_prefix)  # color is ?
        # Don't need to scale workers down as not using eg heroku ps:scale worker=0
        local(
            f"heroku pg:copy {heroku_app_prod}::DATABASE_URL {colour} --app {heroku_app} --confirm {heroku_app}"
        )
        local(f"heroku pg:promote {colour}")
        if clean:
            remove_unused_db(env_prefix)
    finally:
        local("heroku maintenance:off --app {} ".format(heroku_app))


@task
def kill_app(env_prefix, safety_on=True):
    """Kill app notice that to the syntax for the production version is:
    fab kill_app:prod,safety_on=False"""
    if not (
        env_prefix == "prod" and safety_on
    ):  # Safety check - remove when you need to
        heroku_app = "{0}-{1}".format(os.environ["HEROKU_PREFIX"], env_prefix)
        local("heroku destroy {0} --confirm {0}".format(heroku_app))


@task
def first_publish(env_prefix="prod"):
    """Publish to production.  THIS DESTROYS THE OLD BUILD."""
    heroku_app = "{0}-{1}".format(os.environ["HEROKU_PREFIX"], env_prefix)
    os.environ.setdefault("HEROKU_APP", heroku_app)
    kill_app(env_prefix, safety_on=False)
    create_newbuild(env_prefix=env_prefix)
    # local('heroku open')  # opens the web site in a browser window.


# from build.new_db import create_staging, build_staging, update, kill_staging

# @task
def build_staging(env_prefix="uat"):
    """THIS DESTROYS THE OLD BUILD. It builds a new environment with the uat branch."""
    heroku_app = "{0}-{1}".format(os.environ["HEROKU_PREFIX"], env_prefix)
    os.environ.setdefault("HEROKU_APP", heroku_app)
    first_publish(env_prefix)
    transfer_database_from_production(env_prefix)
    # At this stage should have a copy of the master production system
    update_app(env_prefix)
    # local('heroku open')  # opens the web site in a browser window.


def load_local_data(env_prefix="uat"):
    """Adapt this for own use.  This takes a data file in the local playpen directory (not in git)
    adds it temporarily to local git, pushes it to heroku and uploads.  Then removes the file from git.
    Assumes that the master branch is being used and is uptodate.
    Thanks to Jake Trent https://jaketrent.com/post/django-loaddata-heroku/"""
    local(
        "git add playpen/products.json -f"
    )  # Need to force this as playpen is ignored in .gitignore
    local('git commit -m "Added temporary database data"')
    local("git push heroku master")
    local("git reset --soft HEAD^")  # remove temporary file
    local("git reset HEAD playpen/products.json")
    local("git push origin master")
    local("heroku run python manage.py loaddata playpen/products.json")


@task
def build_uat():
    """Build a new uat environments"""
    build_app()


@task
def build_app(env_prefix="uat"):
    """ "Build a test environment. Default is uat.
    So fab build_app  is equivalent to fab build_app:uat  and to fab build_app:env_prefix=uat
    so can build a test branch with:
        fab build_app:env_prefix=test"""
    start_time = time.time()
    try:
        local(f"fab kill_app:{env_prefix}")
    except:
        if env_prefix != "prod":
            pass  # ignore errors in case original does not exist
        else:
            raise Exception(
                "Must stop if an errror when deleteing a production database."
            )
    local(f"fab create_newbuild:env_prefix={env_prefix},branch={env_prefix}")
    local(f"fab transfer_database_from_production:{env_prefix}")
    # makemigrations should be run locally and the results checked into git
    # Need to migrate the old database schema from the master production database
    local(
        "heroku run \"yes 'yes' | python manage.py migrate\""
    )  # Force deletion of stale content types
    # Calculate time
    end_time = time.time()
    runtime = str(dt.timedelta(seconds=int(end_time - start_time)))
    print(f"Run time = {runtime} Completed at: {dt.datetime.now()}")


@task
def update_prod():
    """ "Update the production environment with latest changes.  Removes UAT as this should now be complete.
    This only works for partial updates.  For a major change in how the build is created you need to build a UAT and then
    promote it to production"""
    start_time = time.time()
    local("fab update_app:prod")
    # Not currently working and a pain when uat is removed as can't then promote it.
    # try:
    #     local('fab kill_app:uat')
    # except:
    #     print('No UAT environment to remove')
    end_time = time.time()
    runtime = str(dt.timedelta(seconds=int(end_time - start_time)))
    print(f"Run time = {runtime}")


@task
def update_prod():
    """ "Update the production environment with latest changes.  Removes UAT as this should now be complete.
    THIS ONLY WORKS FOR CODE UPADATE NOT **HEROKU CONFIGURATION CHANGES**.  For a major change in how the build is
    created you need to build a UAT and then promote it to production.  See promote_uat"""
    start_time = time.time()
    local("fab update_app:prod")
    try:
        local("fab kill_app:uat")
    except:
        print("No UAT environment to remove")
    end_time = time.time()
    runtime = str(dt.timedelta(seconds=int(end_time - start_time)))
    print(f"Run time = {runtime}")


@task
def update_requirements():
    """ "After altering requirements eg base.txt or local.txt update the local environment"""
    local("pip install -r requirements/local.txt")


@task
def promote_uat():
    """Promotes UAT to PROD and renames app-prod app-old-prod"""
    old_prod = "{0}-{1}".format(os.environ["HEROKU_PREFIX"], "old-prod")
    prod = "{0}-{1}".format(os.environ["HEROKU_PREFIX"], "prod")
    uat = "{0}-{1}".format(os.environ["HEROKU_PREFIX"], "uat")
    start_time = time.time()
    local(f"heroku maintenance:on --app {prod}")
    try:
        local(
            f"heroku apps:rename {old_prod} --app {prod}"
        )  # Should fail if alread an old_prod
        local(f"heroku apps:rename {prod} --app {uat}")
        # Update allowed site
        local(
            f'heroku config:set DJANGO_ALLOWED_HOSTS="{old_prod}.herokuapp.com" --app {old_prod}'
        )
        local(
            f'heroku config:set DJANGO_ALLOWED_HOSTS="{prod}.herokuapp.com" --app {prod}'
        )
        # Switch over domains
        local(f"heroku domains:clear --app {old_prod}")
        local(f"heroku domains:add bene.drummonds.net --app {prod}")
    finally:
        local(
            f"heroku maintenance:off --app {prod} "
        )  # Different prod does this matter?
        end_time = time.time()
        runtime = str(dt.timedelta(seconds=int(end_time - start_time)))
        print(f"Run time = {runtime}")
