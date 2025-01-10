from typing import Optional, cast

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Configurations
from flamapy.metamodels.configuration_metamodel.models import Configuration
from flamapy.metamodels.bdd_metamodel.models import BDDModel


class BDDConfigurations(Configurations):
    """It computes all the solutions of a BDD model.

    It also supports the computation of all solutions from a partial configuration.
    """

    def __init__(self) -> None:
        self._result: list[Configuration] = []
        self._partial_configuration: Optional[Configuration] = None

    def set_partial_configuration(self, partial_configuration: Configuration) -> None:
        self._partial_configuration = partial_configuration

    def execute(self, model: VariabilityModel) -> 'BDDConfigurations':
        bdd_model = cast(BDDModel, model)
        self._result = configurations(bdd_model, self._partial_configuration)
        return self

    def get_result(self) -> list[Configuration]:
        return self._result

    def get_configurations(self) -> list[Configuration]:
        return self.get_result()


def configurations(bdd_model: BDDModel,
                   partial_config: Optional[Configuration] = None) -> list[Configuration]:
    if partial_config is None:
        u_func = bdd_model.root
        care_vars = set(bdd_model.variables)
        elements = {}
    else:
        values = dict(partial_config.elements.items())
        u_func = bdd_model.bdd.let(values, bdd_model.root)
        care_vars = set(bdd_model.variables) - set(values.keys())
        elements = partial_config.elements

    configs = []
    for assignment in bdd_model.bdd.pick_iter(u_func, care_vars=care_vars):
        features = {f: True for f in assignment.keys() if assignment[f]}
        features = features | elements
        configs.append(Configuration(features))
    return configs
