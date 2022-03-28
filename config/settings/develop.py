"""
Develop Configurations

- As much as possible like production but unlike UAT which should be a faithful replica has debugging switched on

"""

import logging


from .production import *

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool("DJANGO_DEBUG", default=False)
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG

DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": [
        "debug_toolbar.panels.redirects.RedirectsPanel",
    ],
    "SHOW_TEMPLATE_CONTEXT": False,
}
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
