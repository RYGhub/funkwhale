from django.core.management.base import BaseCommand, CommandError

from funkwhale_api.common import scripts


class Command(BaseCommand):
    help = "Run a specific script from funkwhale_api/common/scripts/"

    def add_arguments(self, parser):
        parser.add_argument("script_name", nargs="?", type=str)
        parser.add_argument(
            "--noinput",
            "--no-input",
            action="store_false",
            dest="interactive",
            help="Do NOT prompt the user for input of any kind.",
        )

    def handle(self, *args, **options):
        name = options["script_name"]
        if not name:
            return self.show_help()

        available_scripts = self.get_scripts()
        try:
            script = available_scripts[name]
        except KeyError:
            raise CommandError(
                "{} is not a valid script. Run python manage.py script for a "
                "list of available scripts".format(name)
            )

        self.stdout.write("")
        if options["interactive"]:
            message = (
                "Are you sure you want to execute the script {}?\n\n"
                "Type 'yes' to continue, or 'no' to cancel: "
            ).format(name)
            if input("".join(message)) != "yes":
                raise CommandError("Script cancelled.")
        script["entrypoint"](self, **options)

    def show_help(self):
        self.stdout.write("")
        self.stdout.write("Available scripts:")
        self.stdout.write("Launch with: python manage.py <script_name>")
        available_scripts = self.get_scripts()
        for name, script in sorted(available_scripts.items()):
            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS(name))
            self.stdout.write("")
            for line in script["help"].splitlines():
                self.stdout.write("     {}".format(line))
        self.stdout.write("")

    def get_scripts(self):
        available_scripts = [
            k for k in sorted(scripts.__dict__.keys()) if not k.startswith("__")
        ]
        data = {}
        for name in available_scripts:
            module = getattr(scripts, name)
            data[name] = {
                "name": name,
                "help": module.__doc__.strip(),
                "entrypoint": module.main,
            }
        return data
