import os
if 'ON_HEROKU' in os.environ:
    from .settings_heroku import *
else:
    # Try to import the custom settings.py file, which will in turn import one of the deployment targets.
    # If it doesn't exist we assume this is a dev environment and import .settings_dev.
    try:
        from .settings import *
    except ImportError as e:
        if e.msg.startswith('No module named'):
            from .settings_dev import *
        else:
            raise

import django_env_overrides
django_env_overrides.apply_to(globals())
