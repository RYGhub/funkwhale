import acoustid

from dynamic_preferences.registries import global_preferences_registry


class Client(object):
    def __init__(self, api_key):
        self.api_key = api_key

    def match(self, file_path):
        return acoustid.match(self.api_key, file_path, parse=False)

    def get_best_match(self, file_path):
        results = self.match(file_path=file_path)
        MIN_SCORE_FOR_MATCH = 0.8
        try:
            rows = results['results']
        except KeyError:
            return
        for row in rows:
            if row['score'] >= MIN_SCORE_FOR_MATCH:
                return row


def get_acoustid_client():
    manager = global_preferences_registry.manager()
    return Client(api_key=manager['providers_acoustid__api_key'])
