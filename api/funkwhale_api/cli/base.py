import click
import functools


@click.group()
def cli():
    pass


def confirm_action(f, id_var, message_template="Do you want to proceed?"):
    @functools.wraps(f)
    def action(*args, **kwargs):
        if id_var:
            id_value = kwargs[id_var]
            message = message_template.format(len(id_value))
        else:
            message = message_template
        if not kwargs.pop("no_input", False) and not click.confirm(message, abort=True):
            return

        return f(*args, **kwargs)

    return action


def delete_command(
    group,
    id_var="id",
    name="rm",
    message_template="Do you want to delete {} objects? This action is irreversible.",
):
    """
    Wrap a command to ensure it asks for confirmation before deletion, unless the --no-input
    flag is provided
    """

    def decorator(f):
        decorated = click.option("--no-input", is_flag=True)(f)
        decorated = confirm_action(
            decorated, id_var=id_var, message_template=message_template
        )
        return group.command(name)(decorated)

    return decorator


def update_command(
    group,
    id_var="id",
    name="set",
    message_template="Do you want to update {} objects? This action may have irreversible consequnces.",
):
    """
    Wrap a command to ensure it asks for confirmation before deletion, unless the --no-input
    flag is provided
    """

    def decorator(f):
        decorated = click.option("--no-input", is_flag=True)(f)
        decorated = confirm_action(
            decorated, id_var=id_var, message_template=message_template
        )
        return group.command(name)(decorated)

    return decorator
