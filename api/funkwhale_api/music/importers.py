def load(model, *args, **kwargs):
    importer = registry[model.__name__](model=model)
    return importer.load(*args, **kwargs)


EXCLUDE_VALIDATION = {"Track": ["artist"]}


class Importer(object):
    def __init__(self, model):
        self.model = model

    def load(self, cleaned_data, raw_data, import_hooks):
        mbid = cleaned_data.pop("mbid")
        # let's validate data, just in case
        instance = self.model(**cleaned_data)
        exclude = EXCLUDE_VALIDATION.get(self.model.__name__, [])
        instance.full_clean(exclude=["mbid", "uuid", "fid", "from_activity"] + exclude)
        m = self.model.objects.update_or_create(mbid=mbid, defaults=cleaned_data)[0]
        for hook in import_hooks:
            hook(m, cleaned_data, raw_data)
        return m


class Mapping(object):
    """Cast musicbrainz data to funkwhale data and vice-versa"""

    def __init__(self, musicbrainz_mapping):
        self.musicbrainz_mapping = musicbrainz_mapping

        self._from_musicbrainz = {}
        self._to_musicbrainz = {}
        for field_name, conf in self.musicbrainz_mapping.items():
            self._from_musicbrainz[conf["musicbrainz_field_name"]] = {
                "field_name": field_name,
                "converter": conf.get("converter", lambda v: v),
            }
            self._to_musicbrainz[field_name] = {
                "field_name": conf["musicbrainz_field_name"],
                "converter": conf.get("converter", lambda v: v),
            }

    def from_musicbrainz(self, key, value):
        return (
            self._from_musicbrainz[key]["field_name"],
            self._from_musicbrainz[key]["converter"](value),
        )


registry = {"Artist": Importer, "Track": Importer, "Album": Importer}
