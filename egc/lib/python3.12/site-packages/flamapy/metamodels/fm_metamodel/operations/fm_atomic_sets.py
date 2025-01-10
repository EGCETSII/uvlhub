from typing import cast

from flamapy.core.models import VariabilityModel
from flamapy.core.operations.atomic_sets import AtomicSets
from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature


class FMAtomicSets(AtomicSets):

    def __init__(self) -> None:
        self.result: list[set[Feature]] = []

    def get_result(self) -> list[set[Feature]]:
        return self.result

    def execute(self, model: VariabilityModel) -> 'FMAtomicSets':
        fm_model = cast(FeatureModel, model)
        self.result = get_atomic_sets(fm_model)
        return self

    def atomic_sets(self) -> list[set[Feature]]:
        return self.get_result()


def get_atomic_sets(feature_model: FeatureModel) -> list[set[Feature]]:
    # if feature_model.root is None:
    #     return []

    atomic_sets = []
    root = feature_model.root
    atomic_set = {root}
    atomic_sets.append(atomic_set)
    compute_atomic_sets(atomic_sets, root, atomic_set)
    return atomic_sets


def compute_atomic_sets(atomic_sets: list[set[Feature]],
                        feature: Feature,
                        current_set: set[Feature]) -> None:
    for child in feature.get_children():
        if child.is_mandatory():
            current_set.add(child)
            compute_atomic_sets(atomic_sets, child, current_set)
        else:
            new_as = {child}
            atomic_sets.append(new_as)
            compute_atomic_sets(atomic_sets, child, new_as)
