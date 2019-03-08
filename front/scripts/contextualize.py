import argparse
import polib


def get_missing(entries):
    """
    Return a list of entries with:
    - a msgcontext
    - an empty msgstr
    """
    for e in entries:
        if e.translated():
            continue
        yield e
    return []


def match(entries, other_entries):
    """
    Given two list of po entries, will return a list of 2-tuples with
    match from the second list
    """

    by_id = {}
    for e in other_entries:
        is_translated = bool(e.msgstr)
        if not is_translated:
            continue
        by_id[e.msgid] = e

    matches = []
    for e in entries:
        matches.append((e, by_id.get(e.msgid)))

    return matches


def update(new, old):
    """
    Update a new po entry with translation from the first one (removing fuzzy if needed)
    """
    new.msgstr = old.msgstr
    new.flags = [f for f in new.flags if f != "fuzzy"]


def contextualize(old_po, new_po, edit=False):
    old = polib.pofile(old_po)
    new = polib.pofile(new_po)
    missing = list(get_missing(new))
    print(
        "Found {} entries with contexts and missing translations ({} total)".format(
            len(missing), len(new)
        )
    )
    matches = match(missing, old)
    found = [m for m in matches if m[1] is not None]
    print("Found {} matching entries".format(len(found)))
    if edit:
        print("Applying changes")
        for matched, matching in found:
            update(matched, matching)
        new.save()
    else:
        print("--no-dry-run not provided, not applying change")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        Given two .po file paths, it will populate empty contextualized messages
        in the second one with matching message IDs from the first one, if any.

        This is especially helpful when you add some contexts on existing translated strings
        but don't want to have those being retranslated.
    """
    )
    parser.add_argument("old_po", help="Path of the po file to use as a source")
    parser.add_argument("new_po", help="Path of the po file to populate")
    parser.add_argument("--no-dry-run", action="store_true")
    args = parser.parse_args()

    contextualize(old_po=args.old_po, new_po=args.new_po, edit=args.no_dry_run)
