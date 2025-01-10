from typing import cast

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import AverageBranchingFactor
from flamapy.metamodels.fm_metamodel.models.feature_model import FeatureModel


class FMAverageBranchingFactor(AverageBranchingFactor):
    """The average branching factor is the average of branches in the feature model.

    The number of branches is the number of features that have at least one child.
    """

    def __init__(self) -> None:
        self.result: float = 0

    def get_result(self) -> float:
        return self.result

    def execute(self, model: VariabilityModel) -> 'FMAverageBranchingFactor':
        fm_model = cast(FeatureModel, model)
        self.result = average_branching_factor(fm_model)
        return self

    def get_average_branching_factor(self) -> float:
        return self.get_result()


def average_branching_factor(feature_model: FeatureModel, precision: int = 2) -> float:
    nof_branches = 0
    nof_children = 0
    for feature in feature_model.get_features():
        if feature.get_relations():
            nof_branches += 1
            nof_children += sum(len(r.children) for r in feature.get_relations())
    return round(nof_children / nof_branches, precision)
