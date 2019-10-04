#!/usr/bin/env python3

import argparse
import json
import subprocess

from distutils.version import StrictVersion


def get_versions():

    output = subprocess.check_output(
        ["git", "tag", "-l", "--format=%(creatordate:iso-strict)|%(refname:short)"]
    )
    tags = []

    for line in output.decode().splitlines():
        try:
            date, tag = line.split("|")
        except (ValueError):
            continue

        if not date or not tag:
            continue

        tags.append({"id": tag, "date": date})
    valid = []
    for tag in tags:
        try:
            StrictVersion(tag["id"])
            valid.append(tag)
        except ValueError:
            continue

    return sorted(valid, key=lambda tag: StrictVersion(tag["id"]), reverse=True)


def main(latest=False):
    versions = get_versions()
    if latest:
        print(versions[0]["id"])
    else:
        data = {"count": len(versions), "releases": versions}
        print(json.dumps(data, sort_keys=True, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        """
        Compile release data and output in in JSON format
        """
    )
    parser.add_argument(
        "-l",
        "--latest",
        action="store_true",
        help="Only print the latest version then exit",
    )
    args = parser.parse_args()
    main(latest=args.latest)
