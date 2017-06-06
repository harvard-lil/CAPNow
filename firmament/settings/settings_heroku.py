from .settings_common import *

import environ
env = environ.Env()

DEBUG = False

# database
DATABASES['default'] = env.db()

# S3 storage
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'cap-firmament'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

# static assets
WEBPACK_LOADER['DEFAULT'].update({
    'BUNDLE_DIR_NAME': 'dist/',
    'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats-prod.json'),
})

# message passing
# settings via https://www.cloudamqp.com/docs/celery.html
BROKER_POOL_LIMIT=1
BROKER_URL = env('CLOUDAMQP_URL')
BROKER_CONNECTION_TIMEOUT = 30
BROKER_HEARTBEAT = None
CELERY_SEND_EVENTS = False  # on the free CloudAMQP plan, celery events rapidly eat up our monthly message quota
#CELERY_RESULT_BACKEND = env('REDIS_URL')
CELERYD_HIJACK_ROOT_LOGGER = False
