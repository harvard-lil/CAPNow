from .settings_common import *

# use django db for celery backend
INSTALLED_APPS += ('kombu.transport.django', )
BROKER_URL = 'django://'

# django_extensions
try:
    import django_extensions  # noqa
    INSTALLED_APPS += ('django_extensions',)
except ImportError:
    pass