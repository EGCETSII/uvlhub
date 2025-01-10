from typing import cast

from pysat.solvers import Solver

from flamapy.core.operations import Satisfiable

from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.core.models import VariabilityModel


class PySATSatisfiable(Satisfiable):

    def __init__(self) -> None:
        self.result = False
        self.solver = Solver(name='glucose3')

    def is_satisfiable(self) -> bool:
        return self.get_result()

    def get_result(self) -> bool:
        return self.result

    def execute(self, model: VariabilityModel) -> 'PySATSatisfiable':
        sat_model = cast(PySATModel, model)
        self.result = valid(self.solver, sat_model)
        return self


def valid(solver: Solver, model: PySATModel) -> bool:
    for clause in model.get_all_clauses():
        solver.add_clause(clause)
    result = solver.solve()
    solver.delete()
    return result
