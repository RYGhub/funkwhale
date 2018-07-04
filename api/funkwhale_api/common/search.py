import re

from django.db.models import Q


QUERY_REGEX = re.compile('(((?P<key>\w+):)?(?P<value>"[^"]+"|[\S]+))')


def parse_query(query):
    """
    Given a search query such as "hello is:issue status:opened",
    returns a list of dictionnaries discribing each query token
    """
    matches = [m.groupdict() for m in QUERY_REGEX.finditer(query.lower())]
    for m in matches:
        if m["value"].startswith('"') and m["value"].endswith('"'):
            m["value"] = m["value"][1:-1]
    return matches


def normalize_query(
    query_string,
    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
    normspace=re.compile(r"\s{2,}").sub,
):
    """ Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:

        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    """
    return [normspace(" ", (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string, search_fields):
    """ Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    """
    query = None  # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None  # Query to search for a given term in each field
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


def filter_tokens(tokens, valid):
    return [t for t in tokens if t["key"] in valid]


def apply(qs, config_data):
    for k in ["filter_query", "search_query"]:
        q = config_data.get(k)
        if q:
            qs = qs.filter(q)
    return qs


class SearchConfig:
    def __init__(self, search_fields={}, filter_fields={}, types=[]):
        self.filter_fields = filter_fields
        self.search_fields = search_fields
        self.types = types

    def clean(self, query):
        tokens = parse_query(query)
        cleaned_data = {}

        cleaned_data["types"] = self.clean_types(filter_tokens(tokens, ["is"]))
        cleaned_data["search_query"] = self.clean_search_query(
            filter_tokens(tokens, [None, "in"])
        )
        unhandled_tokens = [t for t in tokens if t["key"] not in [None, "is", "in"]]
        cleaned_data["filter_query"] = self.clean_filter_query(unhandled_tokens)
        return cleaned_data

    def clean_search_query(self, tokens):
        if not self.search_fields or not tokens:
            return

        fields_subset = {
            f for t in filter_tokens(tokens, ["in"]) for f in t["value"].split(",")
        } or set(self.search_fields.keys())
        fields_subset = set(self.search_fields.keys()) & fields_subset
        to_fields = [self.search_fields[k]["to"] for k in fields_subset]
        query_string = " ".join([t["value"] for t in filter_tokens(tokens, [None])])
        return get_query(query_string, sorted(to_fields))

    def clean_filter_query(self, tokens):
        if not self.filter_fields or not tokens:
            return

        matching = [t for t in tokens if t["key"] in self.filter_fields]
        queries = [
            Q(**{self.filter_fields[t["key"]]["to"]: t["value"]}) for t in matching
        ]
        query = None
        for q in queries:
            if not query:
                query = q
            else:
                query = query & q
        return query

    def clean_types(self, tokens):
        if not self.types:
            return []

        if not tokens:
            # no filtering on type, we return all types
            return [t for key, t in self.types]
        types = []
        for token in tokens:
            for key, t in self.types:
                if key.lower() == token["value"]:
                    types.append(t)

        return types
