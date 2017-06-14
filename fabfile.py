import boto3
import datetime as dt
from distutils.dir_util import copy_tree
from fabric.api import *
import fabric.contrib.project as project
import mimetypes
import os
# from os.path import normpath
import random
import shutil
import string
import sys
import socketserver
#from pathlib import Path
from unipath import Path

# .Env
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Local path configuration (can be absolute or relative to fabfile)
env.deploy_path = 'output'
DEPLOY_PATH = Path(env.deploy_path).absolute()
LOCAL_SITE_PATH = Path('C:\Sites\www.drummond.info')

# Remote server configuration
production = 'root@localhost:22'
dest_path = '/var/www'

# Rackspace Cloud Files configuration settings
env.cloudfiles_username = 'my_rackspace_username'
env.cloudfiles_api_key = 'my_rackspace_api_key'
env.cloudfiles_container = 'my_cloudfiles_container'

# Github Pages configuration
env.github_pages_branch = "gh-pages"

# Port for `serve`
PORT = 8000

S3_BUCKET='slf-docs'


def clean():
    """Remove generated files"""
    if os.path.isdir(DEPLOY_PATH):
        shutil.rmtree(DEPLOY_PATH)
        os.makedirs(DEPLOY_PATH)

def build():
    """Build local version of site"""
    local('pelican -s pelicanconf.py')

def rebuild():
    """`build` with the delete switch"""
    local('pelican -d -s pelicanconf.py')

def regenerate():
    """Automatically regenerate site upon file modification"""
    local('pelican -r -s pelicanconf.py')

def serve():
    """Serve site at http://localhost:8000/"""
    os.chdir(env.deploy_path)

    class AddressReuseTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    server = AddressReuseTCPServer(('', PORT), ComplexHTTPRequestHandler)

    sys.stderr.write('Serving on port {0} ...\n'.format(PORT))
    server.serve_forever()

def reserve():
    """`build`, then `serve`"""
    build()
    serve()

def preview():
    """Build production version of site"""
    local('pelican -s publishconf.py')

def cf_upload():
    """Publish to Rackspace Cloud Files"""
    rebuild()
    with lcd(DEPLOY_PATH):
        local('swift -v -A https://auth.api.rackspacecloud.com/v1.0 '
              '-U {cloudfiles_username} '
              '-K {cloudfiles_api_key} '
              'upload -c {cloudfiles_container} .'.format(**env))

def s3_upload():
    """Publish to S3"""
    rebuild()
    # get an access token, local (from) directory, and S3 (to) directory
    # from the command-line
    #local_directory = Path(normpath('./output'))
    local_directory = Path('./output').norm()
    print('Local directory = {}',format(local_directory))
    bucket = S3_BUCKET

    client = boto3.client('s3')

    # enumerate local files recursively
    for root, dirs, files in os.walk(local_directory):
        for filename in files:
            # construct the full local path
            local_path = Path(root, filename).norm()
            print('Local path = {}', format(local_path))
            # construct the full S3 path
            s3_path = '/'.join(local_directory.rel_path_to(local_path).components())[1:]
            print('Searching for path "{}" in "{}" for {}'.format(s3_path, bucket, local_path))
            try:
                file = client.head_object(Bucket=bucket, Key=s3_path)
                lt = dt.datetime.utcfromtimestamp(local_path.mtime())
                #print('Local time {} and external time {}'.format(lt,file['LastModified']))
                print("Path found on S3! Skipping {} which has {}...".format(s3_path, file['LastModified']))

                try:
                    client.delete_object(Bucket=bucket, Key=s3_path)
                    print("Uploading %s..." % s3_path)
                    mime_type = mimetypes.guess_type(local_path)
                    client.upload_file(local_path, bucket, s3_path, ExtraArgs={'ContentType': mime_type[0],
                                                                               'ACL': 'public-read'})
                except:
                    print("Unable to delete %s..." % s3_path)
            except:
                print("Uploading %s..." % s3_path)
                mime_type = mimetypes.guess_type(local_path)
                client.upload_file(local_path, bucket, s3_path, ExtraArgs={'ContentType': mime_type[0],
                                                                           'ACL': 'public-read'})
    # s3cmd sync $(OUTPUTDIR)/ s3://$(S3_BUCKET) --acl-public --delete-removed --guess-mime-type --no-mime-magic --no-preserve


@hosts(production)
def publish():
    """Publish to production via rsync"""
    local('pelican -s publishconf.py')
    project.rsync_project(
        remote_dir=dest_path,
        exclude=".DS_Store",
        local_dir=DEPLOY_PATH.rstrip('/') + '/',
        delete=True,
        extra_opts='-c',
    )

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
    local("heroku config:set DJANGO_ALLOWED_HOSTS='.herokuapp.com' --app {}".format(heroku_app))
    local('heroku config:set PYTHONHASHSEED=random --app {}"'.format(heroku_app))
    local('heroku config:set DJANGO_ADMIN_URL=\^bene_admin/ --app {}"'.format(heroku_app))
    local('heroku config:set DJANGO_OPBEAT_ORGANIZATION_ID={} --app {}'
          .format(os.environ['DJANGO_OPBEAT_ORGANIZATION_ID'], heroku_app))
    local('heroku config:set DJANGO_OPBEAT_APP_ID={} --app {}'
          .format(os.environ['DJANGO_OPBEAT_APP_ID'], heroku_app))
    local('heroku config:set DJANGO_OPBEAT_SECRET_TOKEN={} --app {}'
          .format(os.environ['DJANGO_OPBEAT_SECRET_TOKEN'], heroku_app))

    local('heroku git:remote -a {}'.format(heroku_app))
    local('git push heroku master')

def local_publish():
    """Publish to production via copy"""
    local('pelican -s localconf.py')
    try:
        shutil.rmtree(LOCAL_SITE_PATH)
    except FileNotFoundError:
        pass  # doesn't exist
    copy_tree(DEPLOY_PATH, LOCAL_SITE_PATH)
    copy_tree(DEPLOY_PATH.ancestor(2).child(
        'Pelican').child('pelican-bootstrap3').child('static'),
                    LOCAL_SITE_PATH.child('static'))
    copy_tree(DEPLOY_PATH.ancestor(1).child(
        'content').child('images'),
                    LOCAL_SITE_PATH.child('images'))

def gh_pages():
    """Publish to GitHub Pages"""
    rebuild()
    local("ghp-import -b {github_pages_branch} {deploy_path} -p".format(**env))
