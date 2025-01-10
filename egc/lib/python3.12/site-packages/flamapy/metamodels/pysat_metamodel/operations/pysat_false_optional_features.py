import logging
from typing import Any, cast

from pysat.solvers import Solver

from flamapy.core.operations import FalseOptionalFeatures
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.metamodels.fm_metamodel.models.feature_model import FeatureModel
from flamapy.core.models import VariabilityModel, VariabilityElement
from flamapy.core.exceptions import FlamaException


LOGGER = logging.getLogger('PySATFalseOptionalFeatures')


class PySATFalseOptionalFeatures(FalseOptionalFeatures):

    def __init__(self) -> None:
        self.result: list[Any] = []
        self.solver = Solver(name='glucose3')

    def execute(self, model: VariabilityModel) -> 'PySATFalseOptionalFeatures':
        sat_model = cast(PySATModel, model)
        self.result = self._get_false_optional_features(sat_model)
        return self

    def get_false_optional_features(self) -> list[VariabilityElement]:
        return self.get_result()

    def get_result(self) -> list[Any]:
        return self.result

    def _get_false_optional_features(self, sat_model: PySATModel) -> list[Any]:
        try:
            feature_model = cast(FeatureModel, sat_model.original_model)
        except FlamaException:
            LOGGER.exception("The transformation didn't attach the source model, " 
                             "which is required for this operation.")

        real_optional_features = [f for f in feature_model.get_features()
                                  if not f.is_root() and not f.is_mandatory()]

        result = []
        for clause in sat_model.get_all_clauses():
            self.solver.add_clause(clause)

        for feature in real_optional_features:
            variable = sat_model.variables.get(feature.name)
            parent_feature = feature.get_parent()
            if parent_feature is not None:
                parent_variable = sat_model.variables.get(parent_feature.name)
                assert variable is not None
                satisfiable = self.solver.solve(assumptions=[parent_variable, -variable])
                if not satisfiable:
                    result.append(feature)
        self.solver.delete()
        return result
