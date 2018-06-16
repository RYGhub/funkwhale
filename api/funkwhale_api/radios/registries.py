import persisting_theory


class RadioRegistry(persisting_theory.Registry):
    def prepare_name(self, data, name=None):
        setattr(data, "radio_type", name)
        return name


registry = RadioRegistry()
