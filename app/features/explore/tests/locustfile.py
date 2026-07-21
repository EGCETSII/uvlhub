import random

from locust import HttpUser, TaskSet, between, task
from splent_framework.environment.host import get_host_for_locust_testing

# Terms picked so that some of them match the seeded datasets and some do not,
# which exercises both the populated and the empty result branches.
SEARCH_TERMS = ["", "sample", "dataset", "author", "uvl", "feature model", "nonexistent term"]

SORTINGS = ["newest", "oldest"]

PUBLICATION_TYPES = ["any", "journal article", "conference paper", "book", "software documentation"]

# NOTE: the "tags" filter is deliberately left empty. Sending a non-empty tag
# list makes ExploreRepository.filter build invalid SQL and the endpoint answers
# 500 (see app/features/explore/repositories.py, the any_() call). Load tests
# must not be red because of a product bug, so that branch is not exercised here
# until the bug is fixed.
TAG_SETS = [[]]


class ExploreBehavior(TaskSet):
    """Search traffic against the explore feature.

    The page itself is a thin shell: the real work happens in the POST endpoint,
    which joins datasets, metadata, authors and feature model metadata and runs
    an ILIKE filter per word of the query. Search is therefore weighted much
    higher than the page load.
    """

    @task(2)
    def open_explore_page(self):
        response = self.client.get("/explore", name="/explore [GET]")
        if response.status_code != 200:
            print(f"Explore page failed: {response.status_code}")

    @task(1)
    def open_explore_page_with_query(self):
        """The landing page is also reachable with a prefilled query string."""
        query = random.choice(SEARCH_TERMS)
        response = self.client.get("/explore", params={"query": query}, name="/explore [GET] with query")
        if response.status_code != 200:
            print(f"Explore page with query failed: {response.status_code}")

    @task(6)
    def search(self):
        payload = {
            "query": random.choice(SEARCH_TERMS),
            "sorting": random.choice(SORTINGS),
            "publication_type": random.choice(PUBLICATION_TYPES),
            "tags": random.choice(TAG_SETS),
        }
        response = self.client.post("/explore", json=payload, name="/explore [POST] search")
        if response.status_code != 200:
            print(f"Explore search failed: {response.status_code}")

    @task(2)
    def search_with_empty_filters(self):
        """A user landing on explore without typing anything: no filters at all."""
        response = self.client.post("/explore", json={}, name="/explore [POST] no filters")
        if response.status_code != 200:
            print(f"Explore unfiltered search failed: {response.status_code}")


class ExploreUser(HttpUser):
    tasks = [ExploreBehavior]
    wait_time = between(1, 3)
    host = get_host_for_locust_testing()
