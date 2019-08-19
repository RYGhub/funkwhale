#!/usr/bin/env python3
import argparse
import json
import sys
from distutils.version import StrictVersion


def main(current, releases_json):
    try:
        version = StrictVersion(current)
    except ValueError:
        print("Version number '{}' isn't valid".format(current))
        sys.exit(1)

    releases = json.loads(releases_json)
    latest_release = releases["releases"][0]["id"]

    if version != latest_release:
        print(
            "Version number '{}' doesn't match latest release {}".format(
                current, latest_release
            )
        )
        sys.exit(1)
    print("Version number '{}' is latest release!".format(current))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        Exit with code 0 if the given version matches the latest one
        fron the list of releases found in releases_json. Primary use
        is to check whether the current version can be safely pushed
        as the latest one on the docker Hub.
    """
    )
    parser.add_argument("current", help="Current version")
    parser.add_argument("releases_json", type=argparse.FileType("r"))
    args = parser.parse_args()
    main(args.current, args.releases_json.read())
