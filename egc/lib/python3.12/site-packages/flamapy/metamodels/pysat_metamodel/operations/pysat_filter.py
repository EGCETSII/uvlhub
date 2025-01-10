from typing import Any, cast

from pysat.solvers import Solver

from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.core.operations import Filter
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.core.models import VariabilityModel


class PySATFilter(Filter):

    def __init__(self) -> None:
        self.filter_products: list[list[Any]] = []
        self.configuration = Configuration({})
        self.solver = Solver(name='glucose3')

    def get_filter_products(self) -> list[list[Any]]:
        return self.filter_products

    def get_result(self) -> list[list[Any]]:
        return self.get_filter_products()

    def set_configuration(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def execute(self, model: VariabilityModel) -> 'PySATFilter':
        model = cast(PySATModel, model)

        for clause in model.get_all_clauses():  # AC es conjunto de conjuntos
            self.solver.add_clause(clause)  # añadimos la constraint

        assumptions = []
        for feat in self.configuration.elements.items():
            variable = model.variables.get(feat[0])
            if variable is not None:
                if feat[1]:
                    assumptions.append(variable)
                else:
                    assumptions.append(-variable)

        for solution in self.solver.enum_models(assumptions=assumptions):
            product = []
            for variable in solution:
                if variable is not None and variable > 0:
                    product.append(model.features.get(variable))
            self.filter_products.append(product)
        self.solver.delete()
        return self
