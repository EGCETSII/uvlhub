from typing import cast

from pysat.solvers import Solver

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import SatisfiableConfiguration
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class PySATSatisfiableConfiguration(SatisfiableConfiguration):

    def __init__(self) -> None:
        self.result = False
        self.configuration = Configuration(elements={})
        self.solver = Solver(name='glucose3')
        self.is_full = False

    def is_satisfiable(self) -> bool:
        return self.result

    def get_result(self) -> bool:
        return self.is_satisfiable()

    def set_configuration(self, configuration: Configuration, is_full: bool) -> None:
        self.configuration = configuration
        self.is_full = is_full

    def execute(self, model: VariabilityModel) -> 'PySATSatisfiableConfiguration':
        sat_model = cast(PySATModel, model)
        
        for clause in sat_model.get_all_clauses():  # AC es conjunto de conjuntos
            self.solver.add_clause(clause)  # añadimos la constraint
    
        if not self.is_full:
            assumptions = []
            for feature, selected in self.configuration.elements.items():
                if selected:
                    assumptions.append(sat_model.variables[feature])
                else:
                    assumptions.append(-sat_model.variables[feature])
        else:
            missing_features = [feature for feature in self.configuration.elements.keys() if feature not in sat_model.variables.keys()]
            
            if missing_features:
                print("The features that are missing are:", [feature for feature in missing_features])
                print("The feature model contains the following features:", list(sat_model.variables.keys()))
                self.result = False
                return self
            

            assumptions = []
            for feature in sat_model.features.values():
                
                if feature in self.configuration.elements.keys():
                    assumptions.append(sat_model.variables[feature])
                else:
                    assumptions.append(-sat_model.variables[feature])

        self.result = self.solver.solve(assumptions=assumptions)
        self.solver.delete()
        return self
