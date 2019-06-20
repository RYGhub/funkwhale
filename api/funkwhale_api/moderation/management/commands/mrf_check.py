import json
import sys
import uuid
import logging

from django.core.management.base import BaseCommand, CommandError
from django.core import validators

from django.conf import settings

from funkwhale_api.common import session
from funkwhale_api.federation import models
from funkwhale_api.moderation import mrf


def is_uuid(v):
    try:
        uuid.UUID(v)
    except ValueError:
        return False
    return True


def is_url(v):
    validator = validators.URLValidator()
    try:
        validator(v)
    except (ValueError, validators.ValidationError):
        return False

    return True


class Command(BaseCommand):
    help = "Check a given message against all or a specific MRF rule"

    def add_arguments(self, parser):
        parser.add_argument(
            "type",
            type=str,
            choices=["inbox"],
            help=("The type of MRF. Only inbox is supported at the moment"),
        )
        parser.add_argument(
            "input",
            nargs="?",
            help=(
                "The path to a file containing JSON data. Use - to read from stdin. "
                "If no input is provided, registered MRF policies will be listed "
                "instead.",
            ),
        )
        parser.add_argument(
            "--policy",
            "-p",
            dest="policies",
            nargs="+",
            default=False,
            help="Restrict to a list of MRF policies that will be applied, in that order",
        )

    def handle(self, *args, **options):
        logger = logging.getLogger("funkwhale.mrf")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler(stream=sys.stderr))

        input = options["input"]
        if not input:
            registry = getattr(mrf, options["type"])
            self.stdout.write(
                "No input given, listing registered policies for '{}' MRF:".format(
                    options["type"]
                )
            )
            for name in registry.keys():
                self.stdout.write("- {}".format(name))
            return
        raw_content = None
        content = None
        if input == "-":
            raw_content = sys.stdin.read()
        elif is_uuid(input):
            self.stderr.write("UUID provided, retrieving payload from db")
            content = models.Activity.objects.get(uuid=input).payload
        elif is_url(input):
            response = session.get_session().get(
                input,
                timeout=5,
                verify=settings.EXTERNAL_REQUESTS_VERIFY_SSL,
                headers={"Content-Type": "application/activity+json"},
            )
            response.raise_for_status()
            content = response.json()
        else:
            with open(input, "rb") as f:
                raw_content = f.read()
        content = json.loads(raw_content) if content is None else content

        policies = options["policies"] or []
        registry = getattr(mrf, options["type"])
        for policy in policies:
            if policy not in registry:
                raise CommandError(
                    "Unknown policy '{}' for MRF '{}'".format(policy, options["type"])
                )

        payload, updated = registry.apply(content, policies=policies)
        if not payload:
            self.stderr.write("Payload was discarded by MRF")
        elif updated:
            self.stderr.write("Payload was modified by MRF")
            self.stderr.write("Initial payload:\n")
            self.stdout.write(json.dumps(content, indent=2, sort_keys=True))
            self.stderr.write("Modified payload:\n")
            self.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
        else:
            self.stderr.write("Payload left untouched by MRF")
