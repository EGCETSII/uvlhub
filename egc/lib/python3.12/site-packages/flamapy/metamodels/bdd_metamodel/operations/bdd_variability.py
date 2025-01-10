from typing import cast

from flamapy.core.models import VariabilityModel
from flamapy.metamodels.bdd_metamodel.models import BDDModel
from flamapy.metamodels.bdd_metamodel.operations.interfaces import Variability
from flamapy.metamodels.bdd_metamodel.operations import (
    BDDConfigurationsNumber, 
    BDDVariantFeatures
)


class BDDVariability(Variability):

    def __init__(self) -> None:
        self._result: tuple[float, float] = (0.0, 0.0)

    def execute(self, model: VariabilityModel) -> 'BDDVariability':
        bdd_model = cast(BDDModel, model)
        self._result = variability(bdd_model)
        return self

    def get_result(self) -> tuple[float, float]:
        return self._result

    def total_variability(self) -> float:
        return self.get_result()[0]

    def partial_variability(self) -> float:
        return self.get_result()[1]


def variability(bdd_model: BDDModel) -> tuple[float, float]:
    n_configs = BDDConfigurationsNumber().execute(bdd_model).get_result()
    total_variability = n_configs / (2**len(bdd_model.variables) - 1)
    variant_features = BDDVariantFeatures().execute(bdd_model).get_result()
    partial_variability = n_configs / (2**len(variant_features) - 1)
    return (total_variability, partial_variability)
