web: gunicorn config.wsgi:application
worker: celery worker --app=bene.celery.app --loglevel=info

