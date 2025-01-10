from typing import Any, cast, Optional

from pysat.solvers import Solver

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Sampling
from flamapy.core.exceptions import FlamaException
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class PySATSampling(Sampling):

    def __init__(self) -> None:
        self.result: list[Configuration] = []
        self.sample_size: int = 0
        self.with_replacement: bool = False
        self.partial_configuration: Configuration = None
        self.solver = Solver(name='glucose3')

    def set_sample_size(self, sample_size: int) -> None:
        if sample_size < 0:
            raise FlamaException(f'Sample size {sample_size} cannot be negative.')
        self.sample_size = sample_size

    def set_with_replacement(self, with_replacement: bool) -> None:
        self.with_replacement = with_replacement

    def set_partial_configuration(self, partial_configuration: Configuration) -> None:
        self.partial_configuration = partial_configuration

    def get_sample(self) -> list[Configuration]:
        return self.get_result()

    def get_result(self) -> list[Configuration]:
        return self.result

    def execute(self, model: VariabilityModel) -> 'PySATSampling':
        sat_model = cast(PySATModel, model)
        self.result = sample(self.solver, 
                             sat_model, 
                             self.sample_size, 
                             self.with_replacement, 
                             self.partial_configuration)
        return self


def sample(solver: Solver,
           model: PySATModel, 
           sample_size: int, 
           with_replacement: bool,  # pylint: disable=unused-argument
           partial_configuration: Optional[Configuration]  # pylint: disable=unused-argument
           ) -> list[Configuration]:
    if sample_size == 0:
        return []

    for clause in model.get_all_clauses():
        solver.add_clause(clause)

    products = []
    for solutions in solver.enum_models():
        product: dict[Any, bool] = {}
        for variable in solutions:
            if variable > 0:
                product[model.features.get(variable)] = True
        products.append(Configuration(product))
        if len(products) == sample_size:
            solver.delete()
            return products
    solver.delete()
    return products
