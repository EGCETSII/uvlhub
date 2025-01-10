from typing import cast

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Operation
from flamapy.metamodels.fm_metamodel.models import FeatureModel
from flamapy.metamodels.fm_metamodel.operations.fm_feature_ancestors import get_feature_ancestors
from flamapy.metamodels.fm_metamodel.operations.fm_leaf_features import get_leaf_features


class FMMaxDepthTree(Operation):
    """This operation returns the maximum depth of the feature model tree."""

    def __init__(self) -> None:
        self.result = 0

    def get_result(self) -> int:
        return self.result

    def execute(self, model: VariabilityModel) -> 'FMMaxDepthTree':
        fm_model = cast(FeatureModel, model)
        self.result = max_depth_tree(fm_model)
        return self


def max_depth_tree(feature_model: FeatureModel) -> int:
    return max(len(get_feature_ancestors(f)) for f in get_leaf_features(feature_model))
