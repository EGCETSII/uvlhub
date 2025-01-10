from typing import cast

from pysat.solvers import Solver

from flamapy.core.operations import ConfigurationsNumber
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.core.models import VariabilityModel


class PySATConfigurationsNumber(ConfigurationsNumber):

    def __init__(self) -> None:
        self.products_number = 0
        self.solver = Solver(name='glucose3')

    def get_configurations_number(self) -> int:
        return self.products_number

    def get_result(self) -> int:
        return self.get_configurations_number()

    def execute(self, model: VariabilityModel) -> 'PySATConfigurationsNumber':
        model = cast(PySATModel, model)

        for clause in model.get_all_clauses():  # AC es conjunto de conjuntos
            self.solver.add_clause(clause)  # añadimos la constraint

        for _ in self.solver.enum_models():
            self.products_number += 1
        self.solver.delete()
        return self
