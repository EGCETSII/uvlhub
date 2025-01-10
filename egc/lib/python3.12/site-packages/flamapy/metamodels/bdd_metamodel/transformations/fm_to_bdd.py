from typing import Optional

from flamapy.core.transformations import ModelToModel
from flamapy.metamodels.fm_metamodel.models import FeatureModel
from flamapy.metamodels.bdd_metamodel.models import BDDModel
from flamapy.metamodels.bdd_metamodel.transformations.fm_to_bdd_pl import FmToBDD as FmToBddPL
from flamapy.metamodels.bdd_metamodel.transformations.fm_to_bdd_cnf import FmToBDD as FmToBddCNF


class FmToBDD(ModelToModel):

    @staticmethod
    def get_source_extension() -> str:
        return "fm"

    @staticmethod
    def get_destination_extension() -> str:
        return "bdd"

    def __init__(self, source_model: FeatureModel) -> None:
        self.source_model = source_model
        self.destination_model: Optional[BDDModel] = None

    def transform(self) -> BDDModel:
        try:
            bdd_model = FmToBddPL(self.source_model).transform()
        except BaseException:
            bdd_model = FmToBddCNF(self.source_model).transform()
        return bdd_model
