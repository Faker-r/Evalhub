from celery import Celery

from api.core.config import settings


def create_celery_app() -> Celery:
    app = Celery(
        "evalhub",
        broker=settings.REDIS_URL,
        backend=None,
        include=["api.evaluations.tasks"],
    )

    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        task_ignore_result=True,
        worker_prefetch_multiplier=1,
        task_soft_time_limit=3600,
        task_time_limit=3900,
    )

    return app


celery_app = create_celery_app()
