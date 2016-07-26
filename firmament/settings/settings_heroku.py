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

# message passing
# settings via https://www.cloudamqp.com/docs/celery.html
BROKER_POOL_LIMIT=1
BROKER_URL = env('CLOUDAMQP_URL')
BROKER_CONNECTION_TIMEOUT = 30
BROKER_HEARTBEAT = 30
CELERY_SEND_EVENTS = False  # on the free CloudAMQP plan, celery events rapidly eat up our monthly message quota
CELERY_RESULT_BACKEND = env('REDIS_URL')
CELERYD_HIJACK_ROOT_LOGGER = False

# logging
LOGGING['handlers']['default'] = {
    'level': 'INFO',
    'class': 'logging.StreamHandler',
    'formatter': 'standard',
}