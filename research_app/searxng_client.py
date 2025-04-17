import os
import requests

class SearxngClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.environ.get("SEARXNG_HOST", "http://searxng:8080")

    def search(self, query, categories=None, engines=None, language=None, time_range=None):
        params = {"q": query, "format": "json"}
        if categories:
            params["categories"] = categories
        if engines:
            params["engines"] = engines
        if language:
            params["language"] = language
        if time_range:
            params["time_range"] = time_range
        resp = requests.get(f"{self.base_url}/search", params=params)
        resp.raise_for_status()
        return resp.json()
