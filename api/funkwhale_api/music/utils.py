import magic
import mimetypes
import re

from django.db.models import Q


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:

        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    '''
    query = None # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def guess_mimetype(f):
    b = min(100000, f.size)
    t = magic.from_buffer(f.read(b), mime=True)
    if t == 'application/octet-stream':
        # failure, we try guessing by extension
        mt, _ = mimetypes.guess_type(f.path)
        if mt:
            t = mt
    return t


def compute_status(jobs):
    statuses = jobs.order_by().values_list('status', flat=True).distinct()
    errored = any([status == 'errored' for status in statuses])
    if errored:
        return 'errored'
    pending = any([status == 'pending' for status in statuses])
    if pending:
        return 'pending'
    return 'finished'


AUDIO_EXTENSIONS_AND_MIMETYPE = [
    ('ogg', 'audio/ogg'),
    ('mp3', 'audio/mpeg'),
    ('flac', 'audio/x-flac'),
]

EXTENSION_TO_MIMETYPE = {ext: mt for ext, mt in AUDIO_EXTENSIONS_AND_MIMETYPE}
MIMETYPE_TO_EXTENSION = {mt: ext for ext, mt in AUDIO_EXTENSIONS_AND_MIMETYPE}


def get_ext_from_type(mimetype):
    return MIMETYPE_TO_EXTENSION.get(mimetype)


def get_type_from_ext(extension):
    if extension.startswith('.'):
        # we remove leading dot
        extension = extension[1:]
    return EXTENSION_TO_MIMETYPE.get(extension)
