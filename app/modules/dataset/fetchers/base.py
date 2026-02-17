from __future__ import annotations

from abc import ABC, abstractmethod


class FetchError(RuntimeError):
    pass


class Fetcher_Interface(ABC):
    @abstractmethod
    def supports(self, url): ...

    @abstractmethod
    def fetch(self, url, dest_root, current_user=None): ...
