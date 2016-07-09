from .settings_common import *

# use django db for celery backend
INSTALLED_APPS += ('kombu.transport.django', )
BROKER_URL = 'django://'