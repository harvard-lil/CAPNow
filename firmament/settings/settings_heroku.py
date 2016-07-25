from .settings_common import *

import environ
env = environ.Env()

DEBUG = False

DATABASES['default'] = env.db()

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

WEBPACK_LOADER['DEFAULT'].update({
    'BUNDLE_DIR_NAME': 'dist/',
    'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats-prod.json'),
})