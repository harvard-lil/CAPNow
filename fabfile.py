import os

from fabric.api import local

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'firmament.settings')
try:
    django.setup()
except Exception as e:
    print("WARNING: Can't configure Django. %s" % e)

def stop():
    local("killall python")
    local("killall node")

def run():
    local("node dev_assets_server.js &")
    local("python manage.py runserver 127.0.0.1:9000")

def init_db():
    from firmament.models import Series
    local("python manage.py migrate")
    Series(short_name="Mass.").save()

def test_front_matter():
    from firmament.models import Volume
    Volume.objects.first().generate_front_matter()