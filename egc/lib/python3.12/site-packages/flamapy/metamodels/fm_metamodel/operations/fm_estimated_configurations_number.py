import math
from typing import Optional, cast

from flamapy.core.models import VariabilityModel
from flamapy.core.exceptions import FlamaException
from flamapy.core.operations import EstimatedConfigurationsNumber
from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature


class FMEstimatedConfigurationsNumber(EstimatedConfigurationsNumber):
    """It computes an estimation of the number of products of the feature model.

    It only uses the structure of the feature model,
    without taking into account the cross-tree constraints,
    and thus, the number is an upper limit of the real number of products.
    """

    def __init__(self) -> None:
        self.result = 0
        self.feature_model: Optional[FeatureModel] = None

    def execute(self, model: VariabilityModel) -> 'FMEstimatedProductsNumber':
        self.feature_model = cast(FeatureModel, model)
        self.result = self.get_configurations_number()
        return self

    def get_result(self) -> int:
        return self.result

    def get_configurations_number(self) -> int:
        if self.feature_model is None:
            raise FlamaException("The feature model is not defined")

        return count_configurations(self.feature_model)


def count_configurations(feature_model: FeatureModel) -> int:
    return count_configurations_rec(feature_model.root)


def count_configurations_rec(feature: Feature) -> int:
    if feature.is_leaf():
        return 1
    counts = []
    for relation in feature.get_relations():
        if relation.is_mandatory():
            counts.append(count_configurations_rec(relation.children[0]))
        elif relation.is_optional():
            counts.append(count_configurations_rec(relation.children[0]) + 1)
        elif relation.is_alternative():
            counts.append(sum((count_configurations_rec(f) for f in relation.children)))
        elif relation.is_or():
            children_counts = [count_configurations_rec(f) + 1 for f in relation.children]
            counts.append(math.prod(children_counts) - 1)
    return math.prod(counts)
