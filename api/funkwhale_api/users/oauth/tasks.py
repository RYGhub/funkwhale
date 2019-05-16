from funkwhale_api.taskapp import celery

from oauth2_provider import models as oauth2_models


@celery.app.task(name="oauth.clear_expired_tokens")
def clear_expired_tokens():
    oauth2_models.clear_expired()
