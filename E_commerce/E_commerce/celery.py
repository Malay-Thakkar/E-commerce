# project/celery.py

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_commerce.settings')

app = Celery('E_commerce')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
