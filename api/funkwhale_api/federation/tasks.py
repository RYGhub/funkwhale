from requests.exceptions import RequestException

from funkwhale_api.taskapp import celery

from . import library as lb
from . import models


@celery.app.task(
    name='federation.scan_library',
    autoretry_for=[RequestException],
    retry_backoff=30,
    max_retries=5)
@celery.require_instance(models.Library, 'library')
def scan_library(library, until=None):
    if not library.federation_enabled:
        return

    data = lb.get_library_data(library.url)
    scan_library_page.delay(
        library_id=library.id, page_url=data['first'], until=until)


@celery.app.task(
    name='federation.scan_library_page',
    autoretry_for=[RequestException],
    retry_backoff=30,
    max_retries=5)
@celery.require_instance(models.Library, 'library')
def scan_library_page(library, page_url, until=None):
    if not library.federation_enabled:
        return

    data = lb.get_library_page(library, page_url)
    lts = []
    for item_serializer in data['items']:
        item_date = item_serializer.validated_data['published']
        if until and item_date < until:
            return
        lts.append(item_serializer.save())

    next_page = data.get('next')
    if next_page and next_page != page_url:
        scan_library_page.delay(library_id=library.id, page_url=next_page)
