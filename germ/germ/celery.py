import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'germ.settings')
app = Celery('germ')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # Execution tous les matins à 5h00
    'cloture-emprunt-non-empruntes-quotidien': {
        'task': 'materiel.tasks.cloture_emprunt_non_empruntes',
        'schedule': crontab(minute=0, hour=5),
    },
}