from typing import cast

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import CoreFeatures
from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature


class FMCoreFeatures(CoreFeatures):
    """Core features are features that are present in all configurations of the feature model.

    This implementation assumes that:
        (1) there are not any dead-features in the model.
        (2) there are not any false-optional features in the model.

    These assumptions imply that there are not any cross-tree constraints
    involving the core features, otherwise the model would contain:
        dead-features (e.g., for 'excludes' constraints) and
        false-optional features (e.g., for 'requires' constraints).
    """

    def __init__(self) -> None:
        self.result: list[Feature] = []

    def get_result(self) -> list[Feature]:
        return self.result

    def execute(self, model: VariabilityModel) -> 'FMCoreFeatures':
        fm_model = cast(FeatureModel, model)
        self.result = get_core_features(fm_model)
        return self

    def get_core_features(self) -> list[Feature]:
        return self.get_result()


def get_core_features(feature_model: FeatureModel) -> list[Feature]:
    # if feature_model.root is None:
    #     return []

    # Get core features from the tree structure
    core_features = [feature_model.root]
    features = [feature_model.root]
    while features:
        feature = features.pop()
        for relation in feature.get_relations():
            if relation.is_mandatory():
                core_features.extend(relation.children)
                features.extend(relation.children)

    return core_features

    # Get core features from the cross-tree constraints (this takes a while)
    # requires_ctcs = feature_model.get_requires_constraints()
    # new_core_features = core_features
    # while new_core_features:
    #     new_core_features = []
    #     for ctc in requires_ctcs:
    #         ctc_cnf = ctc.ast.to_cnf()
    #         left_node = ctc_cnf.root.left
    #         right_node = ctc_cnf.root.right
    #         if left_node.is_op():
    #             left = left_node.left.data
    #             right = right_node.data
    #         elif right_node.is_op():
    #             left = right_node.left.data
    #             right = left_node.data
    #         left_feature = feature_model.get_feature_by_name(left)
    #         right_feature = feature_model.get_feature_by_name(right)
    #         if left_feature in core_features and right_feature not in core_features:
    #             new_core_features.append(right_feature)
    #             core_features.append(right_feature)
