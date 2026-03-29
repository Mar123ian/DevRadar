from celery import shared_task

@shared_task(name="devradar.tasks.add")
def add(x, y):
    return x + y