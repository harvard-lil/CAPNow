import os
import signal

import sys
from fabric.api import local

import django
from subprocess import Popen

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'firmament.settings')
try:
    django.setup()
except Exception as e:
    print("WARNING: Can't configure Django. %s" % e)

def stop():
    local("killall python")
    local("killall node")

def run():
    commands = [
        'node dev_assets_server.js',
        'celery -A firmament worker --loglevel=info -B'
    ]

    proc_list = [Popen(command, shell=True, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr) for command in commands]
    try:
        local("python manage.py runserver 127.0.0.1:9001")
    finally:
        for proc in proc_list:
            os.kill(proc.pid, signal.SIGKILL)

def init_db():
    from firmament.models import Series
    local("python manage.py migrate")
    Series(name_abbreviation="Mass.").save()

def test_front_matter():
    from firmament.models import Volume
    Volume.objects.first().generate_front_matter()