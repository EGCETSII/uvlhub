from typing import cast

from flamapy.core.models import VariabilityModel
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.bdd_metamodel.models import BDDModel
from flamapy.metamodels.bdd_metamodel.operations.interfaces import Homogeneity
from flamapy.metamodels.bdd_metamodel.operations import BDDCommonalityFactor


class BDDHomogeneity(Homogeneity):

    def __init__(self) -> None:
        self._result: float = 0.0

    def execute(self, model: VariabilityModel) -> 'BDDHomogeneity':
        bdd_model = cast(BDDModel, model)
        self._result = homogeneity(bdd_model)
        return self

    def get_result(self) -> float:
        return self._result

    def homogeneity(self) -> float:
        return self.get_result()


def homogeneity(bdd_model: BDDModel) -> float:
    commonality_sum = 0.0
    commonality_op = BDDCommonalityFactor()

    for feature in bdd_model.variables:
        config = Configuration(elements={feature: True})
        commonality_op.set_configuration(config)
        commonality_sum += commonality_op.execute(bdd_model).get_result()
    return commonality_sum / len(bdd_model.variables)
