from splent_framework.services.BaseService import BaseService

from app.features.explore.repositories import ExploreRepository


class ExploreService(BaseService):
    def __init__(self):
        super().__init__(ExploreRepository())

    def filter(self, query="", sorting="newest", publication_type="any", tags=[], **kwargs):
        return self.repository.filter(query, sorting, publication_type, tags, **kwargs)
