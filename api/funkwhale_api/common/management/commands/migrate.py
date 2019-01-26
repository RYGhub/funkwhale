from django.core.management.commands.migrate import Command as BaseCommand


def patch_write(buffer):
    """
    Django is trying to help us when running migrate, by checking we don't have
    model changes not included in migrations. Unfortunately, running makemigrations
    on production instances create unwanted migrations and corrupt the database.

    So we disabled the makemigrations command, and we're patching the
    write method to ensure misleading messages are never shown to the user,
    because https://github.com/django/django/blob/2.1.5/django/core/management/commands/migrate.py#L186
    does not leave an easy way to disable them.
    """
    unpatched = buffer.write

    def p(message, *args, **kwargs):
        if "'manage.py makemigrations'" in message or "not yet reflected" in message:
            return
        return unpatched(message, *args, **kwargs)

    setattr(buffer, "write", p)


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        patch_write(self.stdout)
