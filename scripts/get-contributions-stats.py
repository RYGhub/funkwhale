import argparse
import requests
import os

GITLAB_URL = "https://dev.funkwhale.audio"
GITLAB_PROJECT_ID = 17
WEBLATE_URL = "https://translate.funkwhale.audio"
WEBLATE_COMPONENT_ID = "funkwhale/front"


def get_commits(ref_name, since):
    url = GITLAB_URL + "/api/v4/projects/{}/repository/commits".format(
        GITLAB_PROJECT_ID
    )
    while url:
        response = requests.get(
            url, params={"since": since, "ref_name": ref_name, "per_page": 100}
        )
        response.raise_for_status()

        yield from response.json()

        if "next" in response.links:
            url = response.links["next"]["url"]
        else:
            url = None


def get_commit_stats(commits):
    stats = {"total": 0, "commiters": {}}
    for commit in commits:
        if commit["message"].startswith("Merge branch "):
            continue
        stats["total"] += 1
        try:
            stats["commiters"][commit["author_name"]] += 1
        except KeyError:
            stats["commiters"][commit["author_name"]] = 1

    return stats


def get_tag_date(ref):
    url = GITLAB_URL + "/api/v4/projects/{}/repository/tags/{}".format(
        GITLAB_PROJECT_ID, ref
    )
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data["commit"]["committed_date"]


def get_translations(since):
    url = WEBLATE_URL + "/api/components/{}/changes/".format(WEBLATE_COMPONENT_ID)
    while url:
        response = requests.get(url)
        response.raise_for_status()
        if "next" in response.json():
            url = response.json()["next"]
        else:
            url = None
        for t in response.json()["results"]:
            if t["timestamp"] < since:
                url = None
                break

            yield t


def get_translations_stats(translations):
    stats = {"total": 0, "translators": {}}
    for translation in translations:
        if not translation["author"]:
            continue
            print("translation", translation["action_name"])
            continue
        stats["total"] += 1
        try:
            stats["translators"][translation["author"]] += 1
        except KeyError:
            stats["translators"][translation["author"]] = 1

    return stats


def get_group_usernames(group):
    url = GITLAB_URL + "/api/v4/groups/{}/members".format(group)
    response = requests.get(url, headers={"PRIVATE-TOKEN": os.environ["PRIVATE_TOKEN"]})
    response.raise_for_status()
    data = response.json()
    return [r["name"] for r in data]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ref_name")
    parser.add_argument("last_tag")
    args = parser.parse_args()
    since = get_tag_date(args.last_tag)
    commits = get_commits(args.ref_name, since)
    commits_stats = get_commit_stats(commits)
    groups = [(588, "funkwhale/reviewers-python"), (589, "funkwhale/reviewers-front")]
    reviewers = []
    for id, _ in groups:
        reviewers += get_group_usernames(id)
    print("\nReviewers:\n")
    for reviewer in reviewers:
        print(reviewer)
    commiter_names = commits_stats["commiters"].keys()
    print("\nCommiters:\n")
    for commiter in sorted(commits_stats["commiters"].keys(), key=lambda v: v.upper()):
        print(commiter)
    translations = get_translations(since)
    translations_stats = get_translations_stats(translations)
    translators_ids = sorted(translations_stats["translators"].keys())
    # There is no way to query user/author info via weblate API and we need the names…
    print(
        "\nExecute the following SQL query on the weblate server to get the translators names:"
    )
    print("$ weblate dbshell")
    print(
        "SELECT full_name FROM weblate_auth_user WHERE id in ({});".format(
            ", ".join([str(i) for i in translators_ids])
        )
    )


if __name__ == "__main__":
    main()
