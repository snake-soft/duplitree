import os
import sys
from celery import Celery, signals
from django.core.mail import mail_admins
from django.views.debug import ExceptionReporter

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('proj')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def celery_error_handler(self, task_id, exception, *args, **kwargs):
    subject = f"Celery Task Failure: {task_id}"
    reporter = ExceptionReporter(None, *sys.exc_info())
    traceback_text = reporter.get_traceback_text()
    mail_admins(subject, traceback_text)


signals.task_failure.connect(celery_error_handler)
