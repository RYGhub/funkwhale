import persisting_theory


class ActivityRegistry(persisting_theory.Registry):
    look_into = "activities"

    def _register_for_model(self, model, attr, value):
        key = model._meta.label
        d = self.setdefault(key, {"consumers": []})
        d[attr] = value

    def register_serializer(self, serializer_class):
        model = serializer_class.Meta.model
        self._register_for_model(model, "serializer", serializer_class)
        return serializer_class

    def register_consumer(self, label):
        def decorator(func):
            consumers = self[label]["consumers"]
            if func not in consumers:
                consumers.append(func)
            return func

        return decorator


registry = ActivityRegistry()


def send(obj):
    conf = registry[obj.__class__._meta.label]
    consumers = conf["consumers"]
    if not consumers:
        return
    serializer = conf["serializer"](obj)
    for consumer in consumers:
        consumer(data=serializer.data, obj=obj)
