import gitlab

TOKEN = "CHANGEME"
CLEAN_BEFORE = "2018-07"
gl = gitlab.Gitlab("https://dev.funkwhale.audio", private_token=TOKEN, per_page=100)
project = gl.projects.get("funkwhale/funkwhale")

jobs = project.jobs.list(as_list=False)
total = jobs.total

for job in jobs:
    if job.attributes["ref"] != "develop":
        continue
    if job.attributes["status"] != "success":
        continue
    if job.attributes["tag"] is True:
        continue
    if job.attributes["name"] not in ["build_api", "build_front", "pages"]:
        continue
    if job.attributes["created_at"].startswith(CLEAN_BEFORE):
        continue
    relevant = {
        "ref": job.attributes["ref"],
        "status": job.attributes["status"],
        "tag": job.attributes["tag"],
        "name": job.attributes["name"],
        "created_at": job.attributes["created_at"],
    }
    print("Deleting job {}!".format(job.id), relevant)
    job.erase()
