from splent_framework.repositories.BaseRepository import BaseRepository
from sqlalchemy import func

from app.features.featuremodel.models import FeatureModel, FMMetaData


class FeatureModelRepository(BaseRepository):
    def __init__(self):
        super().__init__(FeatureModel)

    def count_feature_models(self) -> int:
        return self.model.query.with_entities(func.count(self.model.id)).scalar() or 0


class FMMetaDataRepository(BaseRepository):
    def __init__(self):
        super().__init__(FMMetaData)
