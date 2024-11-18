from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.signals import task_failure
from celery.signals import task_prerun, task_postrun

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AurochOnline.settings')

app = Celery('AurochOnline')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Set the maximum number of concurrent tasks
app.conf.worker_concurrency = 2

#The maximum amount of memory (in KB) that each worker subprocess can use
#app.conf.worker_max_memory_per_child = 10485760  
# app.conf.worker_max_memory_per_child = 500  # 单位是 KB

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@task_failure.connect
def task_failure_handler(sender, task_id, exception, **kwargs):
    print(f'Task {task_id} failed due to {exception}')
# @app.task(bind=True, max_retries=3, default_retry_delay=30)
# def my_task(self, *args, **kwargs):
#     try:
#         pass
#     except Exception as exc:
#         raise self.retry(exc=exc)

@task_prerun.connect
def before_task_handler(sender, **kwargs):
    pid = os.getpid()
    print(f"Before task {sender.name} starts. Process ID: {pid}")

@task_postrun.connect
def after_task_handler(sender, **kwargs):
    pid = os.getpid()
    print(f"After task {sender.name} ends. Process ID: {pid}")