import os
import urllib.parse

from locust import HttpLocust, TaskSet, task

JWT_TOKEN = os.environ.get("JWT_TOKEN")

DATA = {"playable": True}
HEADERS = {}
if JWT_TOKEN:
    print("Starting authenticated session")
    HEADERS["authorization"] = "JWT {}".format(JWT_TOKEN)


class WebsiteTasks(TaskSet):
    @task
    def albums(self):
        self.client.get(
            "/api/v1/albums?" + urllib.parse.urlencode(DATA), headers=HEADERS
        )

    @task
    def artists(self):
        self.client.get(
            "/api/v1/artists?" + urllib.parse.urlencode(DATA), headers=HEADERS
        )

    @task
    def tracks(self):
        self.client.get(
            "/api/v1/tracks?" + urllib.parse.urlencode(DATA), headers=HEADERS
        )


class WebsiteUser(HttpLocust):
    task_set = WebsiteTasks
    min_wait = 1000
    max_wait = 3000
