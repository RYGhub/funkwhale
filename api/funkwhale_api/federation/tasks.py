from funkwhale_api.taskapp import celery

from . import library as lb
from . import models


@celery.app.task(name='federation.scan_library')
@celery.require_instance(models.Library, 'library')
def scan_library(library):
    if not library.federation_enabled:
        return

    data = lb.get_library_data(library.url)
    scan_library_page.delay(
        library_id=library.id, page_url=data['first'])


@celery.app.task(name='federation.scan_library_page')
@celery.require_instance(models.Library, 'library')
def scan_library_page(library, page_url):
    if not library.federation_enabled:
        return

    data = lb.get_library_page(library, page_url)
    lts = []
    for item_serializer in data['items']:
        lts.append(item_serializer.save())
