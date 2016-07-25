import environ
env = environ.Env()

DATABASES['default'] = env.db()

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
