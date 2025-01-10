from typing import Any, cast

from pysat.solvers import Solver

from flamapy.core.operations import CoreFeatures
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.core.models import VariabilityModel


class PySATCoreFeatures(CoreFeatures):

    def __init__(self) -> None:
        self.core_features: list[Any] = []
        self.solver = Solver(name='glucose3')

    def get_core_features(self) -> list[Any]:
        return self.core_features

    def get_result(self) -> list[Any]:
        return self.get_core_features()

    def execute(self, model: VariabilityModel) -> 'PySATCoreFeatures':
        model = cast(PySATModel, model)
        for clause in model.get_all_clauses():  # AC es conjunto de conjuntos
            self.solver.add_clause(clause)  # añadimos la constraint

        core_features = []
        if self.solver.solve():
            for variable in model.variables.items():
                if not self.solver.solve(assumptions=[-variable[1]]):
                    core_features.append(variable[0])

        self.core_features = core_features
        self.solver.delete()
        return self
