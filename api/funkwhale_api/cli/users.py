import click

from django.db import transaction

from funkwhale_api.federation import models as federation_models
from funkwhale_api.users import models
from funkwhale_api.users import serializers
from funkwhale_api.users import tasks

from . import base
from . import utils


class FakeRequest(object):
    def __init__(self, session={}):
        self.session = session


@transaction.atomic
def handler_create_user(
    username,
    password,
    email,
    is_superuser=False,
    is_staff=False,
    permissions=[],
    upload_quota=None,
):
    serializer = serializers.RS(
        data={
            "username": username,
            "email": email,
            "password1": password,
            "password2": password,
        }
    )
    utils.logger.debug("Validating user data…")
    serializer.is_valid(raise_exception=True)

    # Override email validation, we assume accounts created from CLI have a valid email
    request = FakeRequest(session={"account_verified_email": email})
    utils.logger.debug("Creating user…")
    user = serializer.save(request=request)
    utils.logger.debug("Setting permissions and other attributes…")
    user.is_staff = is_staff
    user.upload_quota = upload_quota
    user.is_superuser = is_superuser
    for permission in permissions:
        if permission in models.PERMISSIONS:
            utils.logger.debug("Setting %s permission to True", permission)
            setattr(user, "permission_{}".format(permission), True)
        else:
            utils.logger.warn("Unknown permission %s", permission)
    utils.logger.debug("Creating actor…")
    user.actor = models.create_actor(user)
    user.save()
    return user


@transaction.atomic
def handler_delete_user(usernames, soft=True):
    for username in usernames:
        click.echo("Deleting {}…".format(username))
        actor = None
        user = None
        try:
            user = models.User.objects.get(username=username)
        except models.User.DoesNotExist:
            try:
                actor = federation_models.Actor.objects.local().get(
                    preferred_username=username
                )
            except federation_models.Actor.DoesNotExist:
                click.echo("  Not found, skipping")
                continue

        actor = actor or user.actor
        if user:
            tasks.delete_account(user_id=user.pk)
        if not soft:
            click.echo("  Hard delete, removing actor")
            actor.delete()
        click.echo("  Done")


@transaction.atomic
def handler_update_user(usernames, kwargs):
    users = models.User.objects.filter(username__in=usernames)
    total = users.count()
    if not total:
        click.echo("No matching users")
        return

    final_kwargs = {}
    supported_fields = [
        "is_active",
        "permission_moderation",
        "permission_library",
        "permission_settings",
        "is_staff",
        "is_superuser",
        "upload_quota",
        "password",
    ]
    for field in supported_fields:
        try:
            value = kwargs[field]
        except KeyError:
            continue
        final_kwargs[field] = value

    click.echo(
        "Updating {} on {} matching users…".format(
            ", ".join(final_kwargs.keys()), total
        )
    )
    if "password" in final_kwargs:
        new_password = final_kwargs.pop("password")
        for user in users:
            user.set_password(new_password)
        models.User.objects.bulk_update(users, ["password"])
    if final_kwargs:
        users.update(**final_kwargs)
    click.echo("Done!")


@base.cli.group()
def users():
    """Manage users"""
    pass


@users.command()
@click.option("--username", "-u", prompt=True, required=True)
@click.option(
    "-p",
    "--password",
    prompt="Password (leave empty to have a random one generated)",
    hide_input=True,
    envvar="FUNKWHALE_CLI_USER_PASSWORD",
    default="",
    help="If empty, a random password will be generated and displayed in console output",
)
@click.option(
    "-e",
    "--email",
    prompt=True,
    help="Email address to associate with the account",
    required=True,
)
@click.option(
    "-q",
    "--upload-quota",
    help="Upload quota (leave empty to use default pod quota)",
    required=False,
    default=None,
    type=click.INT,
)
@click.option(
    "--superuser/--no-superuser", default=False,
)
@click.option(
    "--staff/--no-staff", default=False,
)
@click.option(
    "--permission", multiple=True,
)
def create(username, password, email, superuser, staff, permission, upload_quota):
    """Create a new user"""
    generated_password = None
    if password == "":
        generated_password = models.User.objects.make_random_password()
    user = handler_create_user(
        username=username,
        password=password or generated_password,
        email=email,
        is_superuser=superuser,
        is_staff=staff,
        permissions=permission,
        upload_quota=upload_quota,
    )
    click.echo("User {} created!".format(user.username))
    if generated_password:
        click.echo("  Generated password: {}".format(generated_password))


@base.delete_command(group=users, id_var="username")
@click.argument("username", nargs=-1)
@click.option(
    "--hard/--no-hard",
    default=False,
    help="Purge all user-related info (allow recreating a user with the same username)",
)
def delete(username, hard):
    """Delete given users"""
    handler_delete_user(usernames=username, soft=not hard)


@base.update_command(group=users, id_var="username")
@click.argument("username", nargs=-1)
@click.option(
    "--active/--inactive",
    help="Mark as active or inactive (inactive users cannot login or use the service)",
    default=None,
)
@click.option("--superuser/--no-superuser", default=None)
@click.option("--staff/--no-staff", default=None)
@click.option("--permission-library/--no-permission-library", default=None)
@click.option("--permission-moderation/--no-permission-moderation", default=None)
@click.option("--permission-settings/--no-permission-settings", default=None)
@click.option("--password", default=None, envvar="FUNKWHALE_CLI_USER_UPDATE_PASSWORD")
@click.option(
    "-q", "--upload-quota", type=click.INT,
)
def update(username, **kwargs):
    """Update attributes for given users"""
    field_mapping = {
        "active": "is_active",
        "superuser": "is_superuser",
        "staff": "is_staff",
    }
    final_kwargs = {}
    for cli_field, value in kwargs.items():
        if value is None:
            continue
        model_field = (
            field_mapping[cli_field] if cli_field in field_mapping else cli_field
        )
        final_kwargs[model_field] = value

    if not final_kwargs:
        raise click.BadArgumentUsage("You need to update at least one attribute")

    handler_update_user(usernames=username, kwargs=final_kwargs)
