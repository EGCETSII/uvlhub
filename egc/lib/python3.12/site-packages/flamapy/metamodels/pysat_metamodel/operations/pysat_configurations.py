from typing import Any, cast

from pysat.solvers import Solver

from flamapy.core.operations import Configurations
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.core.models import VariabilityModel


class PySATConfigurations(Configurations):

    def __init__(self) -> None:
        self.result: list[Configuration] = []
        self.solver = Solver(name='glucose3')

    def get_configurations(self) -> list[Configuration]:
        return self.get_result()

    def get_result(self) -> list[Configuration]:
        return self.result

    def execute(self, model: VariabilityModel) -> 'PySATConfigurations':
        sat_model = cast(PySATModel, model)
        self.result = configurations(self.solver, sat_model)
        return self


def configurations(solver: Solver, model: PySATModel) -> list[Configuration]:
    for clause in model.get_all_clauses():
        solver.add_clause(clause)

    result = []
    for solutions in solver.enum_models():
        product: dict[Any, bool] = {}
        for variable in solutions:
            if variable > 0:
                product[model.features.get(variable)] = True
        result.append(Configuration(product))
    solver.delete()
    return result
