from rest_framework import exceptions


class MalformedPayload(ValueError):
    pass


class MissingSignature(KeyError):
    pass


class BlockedActorOrDomain(exceptions.AuthenticationFailed):
    pass
