from celery import Celery

app = Celery("tasks", broker="redis://localhost")


@app.task
def send_link(link):
    return link
