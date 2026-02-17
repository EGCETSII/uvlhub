import logging
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from git import GitCommandError, Repo

from .base import Fetcher_Interface, FetchError

logger = logging.getLogger(__name__)


class GithubFetcher(Fetcher_Interface):
    def supports(self, url):
        try:
            return urlparse(url).netloc == "github.com"
        except Exception:
            return False

    def fetch(self, url, dest_root, current_user=None):
        owner, repo, branch, subpath = self._parse_github_url(url)
        if not owner or not repo:
            raise FetchError(f"Invalid GitHub URL: {url}")

        tmp_dir = Path(tempfile.mkdtemp(dir=dest_root))
        repo_dir = tmp_dir / f"{owner}__{repo}"

        clone_url = f"https://github.com/{owner}/{repo}.git"
        logger.info(f"[GitHubFetcher] Cloning {clone_url} into {repo_dir}")

        try:
            if branch:
                Repo.clone_from(clone_url, repo_dir, depth=1, branch=branch)
            else:
                Repo.clone_from(clone_url, repo_dir, depth=1)
        except GitCommandError as e:
            raise FetchError(f"Failed to clone repository: {e}")

        if subpath:
            target = repo_dir / subpath
            if not target.exists():
                raise FetchError("The requested subfolder does not exist in the repository")
            return target

        return repo_dir

    def _parse_github_url(self, url):

        parts = urlparse(url)
        if parts.netloc != "github.com":
            return None, None, None, None

        segments = [s for s in parts.path.split("/") if s]
        if len(segments) < 2:
            return None, None, None, None

        owner, repo = segments[0], segments[1]
        if repo.endswith(".git"):
            repo = repo[:-4]

        branch = None
        subpath = None

        if len(segments) >= 4 and segments[2] == "tree":
            branch = segments[3]
            if len(segments) > 4:
                subpath = "/".join(segments[4:])

        return owner, repo, branch, subpath
