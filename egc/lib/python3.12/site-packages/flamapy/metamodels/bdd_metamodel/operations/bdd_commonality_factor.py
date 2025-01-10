from typing import cast

from flamapy.core.models import VariabilityModel
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.bdd_metamodel.models import BDDModel
from flamapy.metamodels.bdd_metamodel.operations.interfaces import CommonalityFactor
from flamapy.metamodels.bdd_metamodel.operations import BDDConfigurationsNumber


class BDDCommonalityFactor(CommonalityFactor):

    def __init__(self) -> None:
        self._result: float = 0.0
        self._configuration: Configuration = Configuration(elements={})

    def set_configuration(self, configuration: Configuration) -> None:
        self._configuration = configuration

    def execute(self, model: VariabilityModel) -> 'BDDCommonalityFactor':
        bdd_model = cast(BDDModel, model)
        self._result = commonality_factor(bdd_model, self._configuration)
        return self

    def get_result(self) -> float:
        return self._result

    def commonality_factor(self) -> float:
        return self.get_result()


def commonality_factor(bdd_model: BDDModel, config: Configuration) -> float:
    configs_number_op = BDDConfigurationsNumber()
    total_configs = configs_number_op.execute(bdd_model).get_result()
    configs_number_op.set_partial_configuration(config)
    n_configs = configs_number_op.execute(bdd_model).get_result()
    return n_configs / total_configs
