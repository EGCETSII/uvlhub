from pathlib import Path

from .base import FetchError


class DataSourceManager:
    def __init__(self, providers):
        self.providers = list(providers)

    def fetch_to_user_temp(self, url, current_user):
        dest_root = Path(current_user.temp_folder())
        dest_root.mkdir(parents=True, exist_ok=True)

        for p in self.providers:
            if p.supports(url):
                return p.fetch(url, dest_root, current_user=current_user)

        raise FetchError(f"No provider supports this URL: {url}")
