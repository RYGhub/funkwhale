import argparse
import collections
import polib


def print_duplicates(path):
    pofile = polib.pofile(path)

    contexts_by_id = collections.defaultdict(list)
    for e in pofile:
        contexts_by_id[e.msgid].append(e.msgctxt)
    count = collections.Counter([e.msgid for e in pofile])
    duplicates = [(k, v) for k, v in count.items() if v > 1]
    for k, v in sorted(duplicates, key=lambda r: r[1], reverse=True):
        print("{} entries - {}:".format(v, k))
        for ctx in contexts_by_id[k]:
            print("  - {}".format(ctx))
        print()

    total_duplicates = sum([v - 1 for _, v in duplicates])
    print("{} total duplicates".format(total_duplicates))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("po", help="Path of the po file to use as a source")
    args = parser.parse_args()

    print_duplicates(path=args.po)
