from typing import Any, Callable, Optional, cast
import statistics

from flamapy.core.exceptions import FlamaException
from flamapy.core.models.variability_model import VariabilityModel
from flamapy.core.operations.metrics_operation import Metrics
from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature
from flamapy.metamodels.fm_metamodel import operations as fm_operations


def metric_method(func: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
    """Decorator to mark a method as a metric method.
    It has the value of the measure, it can also have a size and a ratio.
    Example:
        property name: Abstract Features.
        description: The description of the property
        value (optional): the list of abstract features.
        size (optional): the length of the list.
        ratio (optional): the percentage of abstract features with regards the total
        number of features.
    """
    if not hasattr(func, "_is_metric_method"):
        setattr(func, "_is_metric_method", True)
    return func


class FMMetrics(Metrics):  # pylint: disable=too-many-instance-attributes

    def __init__(self) -> None:
        super().__init__()
        self.model: Optional[FeatureModel] = None
        self.result: list[dict[str, Any]] = []
        self.model_type_extension = "fm"
        self._features: list[Feature] = []
        self._features_by_name: dict[str, Feature] = {}
        self._abstract_features: dict[str, Feature] = {}
        self._concrete_features: dict[str, Feature] = {}
        self._leaf_features: list[str] = []
        self._constraints_per_features: list[int] = []
        self._feature_ancestors: list[int] = []

    def get_result(self) -> list[dict[str, Any]]:
        return self.result

    def calculate_metamodel_metrics(self, model: VariabilityModel) -> list[dict[str, Any]]:
        self.model = cast(FeatureModel, model)

        # Do some basic calculations to speedup the rest
        self._features = self.model.get_features()
        self._features_by_name = {f.name: f for f in self._features}
        self._abstract_features = {f.name: f for f in self._features if f.is_abstract}
        self._concrete_features = {
            f.name: f for f in self._features if not f.is_abstract
        }
        self._leaf_features = [
            f.name for f in self._features if len(f.get_relations()) == 0
        ]
        self._constraints_per_features = self.constraints_per_features(
            self.model, self._features
        )
        self._feature_ancestors = [
            len(self.get_feature_ancestors(self._features_by_name[f]))
            for f in self._leaf_features
        ]

        # Get all methods that are marked with the metric_method decorator
        metric_methods = [
            getattr(self, method_name)
            for method_name in dir(self)
            if callable(getattr(self, method_name))
            and hasattr(getattr(self, method_name), "_is_metric_method")
        ]
        if self.filter is not None:
            metric_methods = [
                method for method in metric_methods if method.__name__ in self.filter
            ]

        return [method() for method in metric_methods]

    # Auxiliary methods
    def constraints_per_features(
        self, fm: FeatureModel, features: list[Feature]  # pylint: disable=invalid-name
    ) -> list[int]:
        _features_per_constraints = []
        _constraints_per_feature = []
        for ctc in fm.get_constraints():
            _features_per_constraints.append(list(ctc.get_features()))

        for feature in features:
            cpf = sum(feature.name in feat for feat in _features_per_constraints)
            _constraints_per_feature.append(cpf)
        return _constraints_per_feature

    def get_feature_ancestors(self, feature: Feature) -> list[Feature]:
        features = []
        parent = feature.get_parent()
        while parent is not None:
            features.append(parent)
            parent = parent.get_parent()
        return features

    # List of methods that returns a feature
    @metric_method
    def features(self) -> dict[str, Any]:
        """Set of features in the feature model."""
        name = "Features"
        _features = list(self._features_by_name.keys())
        result = self.construct_result(
            name=name, doc=self.features.__doc__, result=_features, size=len(_features)
        )
        return result

    @metric_method
    def abstract_features(self) -> dict[str, Any]:
        """Features used to structure the feature model that, however, do not have any
        impact at implementation level."""
        name = "Abstract features"
        _abstract_features = list(self._abstract_features.keys())
        result = self.construct_result(
            name=name,
            doc=self.abstract_features.__doc__,
            result=_abstract_features,
            size=len(_abstract_features),
            ratio=self.get_ratio(_abstract_features, self._features),
        )
        return result

    @metric_method
    def concrete_features(self) -> dict[str, Any]:
        """Features that are mapped to at least one implementation artifact."""
        name = "Concrete features"
        _concrete_features = list(self._concrete_features.keys())
        result = self.construct_result(
            name=name,
            doc=self.concrete_features.__doc__,
            result=_concrete_features,
            size=len(_concrete_features),
            ratio=self.get_ratio(_concrete_features, self._features),
        )
        return result

    @metric_method
    def leaf_features(self) -> dict[str, Any]:
        """Features that have not subfeatures (aka 'primitive features' or 'terminal features')."""
        name = "Leaf features"
        _leaf_features = self._leaf_features
        result = self.construct_result(
            name=name,
            doc=self.leaf_features.__doc__,
            result=_leaf_features,
            size=len(_leaf_features),
            ratio=self.get_ratio(_leaf_features, self._features),
        )
        return result

    @metric_method
    def compound_features(self) -> dict[str, Any]:
        """Features that have subfeatures."""
        name = "Compound features"
        _compound_features = [
            f.name for f in self._features if len(f.get_relations()) > 0
        ]
        result = self.construct_result(
            name=name,
            doc=self.compound_features.__doc__,
            result=_compound_features,
            size=len(_compound_features),
            ratio=self.get_ratio(_compound_features, self._features),
        )
        return result

    @metric_method
    def concrete_compound_features(self) -> dict[str, Any]:
        """Concrete and compound features."""
        name = "Concrete compound features"
        _concrete_compound_features = [
            name
            for name, f in self._concrete_features.items()
            if len(f.get_relations()) > 0
        ]
        result = self.construct_result(
            name=name,
            doc=self.concrete_compound_features.__doc__,
            result=_concrete_compound_features,
            size=len(_concrete_compound_features),
            ratio=self.get_ratio(
                _concrete_compound_features, self.concrete_features()["result"]
            ),
        )
        return result

    @metric_method
    def concrete_leaf_features(self) -> dict[str, Any]:
        """Concrete and leaf features."""
        name = "Concrete leaf features"
        _concrete_leaf_features = [
            name
            for name, f in self._concrete_features.items()
            if len(f.get_relations()) == 0
        ]
        result = self.construct_result(
            name=name,
            doc=self.concrete_leaf_features.__doc__,
            result=_concrete_leaf_features,
            size=len(_concrete_leaf_features),
            ratio=self.get_ratio(
                _concrete_leaf_features, self.concrete_features()["result"]
            ),
        )
        return result

    @metric_method
    def abstract_compound_features(self) -> dict[str, Any]:
        """Abstract and compound features."""
        name = "Abstract compound features"
        _abstract_compound_features = [
            name
            for name, f in self._abstract_features.items()
            if len(f.get_relations()) > 0
        ]
        result = self.construct_result(
            name=name,
            doc=self.abstract_compound_features.__doc__,
            result=_abstract_compound_features,
            size=len(_abstract_compound_features),
            ratio=self.get_ratio(
                _abstract_compound_features, self._abstract_features.keys()
            ),
        )
        return result

    @metric_method
    def abstract_leaf_features(self) -> dict[str, Any]:
        """Abstract and leaf features."""
        name = "Abstract leaf features"
        _abstract_leaf_features = [
            name
            for name, f in self._abstract_features.items()
            if len(f.get_relations()) == 0
        ]
        result = self.construct_result(
            name=name,
            doc=self.abstract_leaf_features.__doc__,
            result=_abstract_leaf_features,
            size=len(_abstract_leaf_features),
            ratio=self.get_ratio(
                _abstract_leaf_features, self._abstract_features.keys()
            ),
        )
        return result

    @metric_method
    def tree_relationships(self) -> dict[str, Any]:
        """Number of relationships (edges) of the feature model."""
        if self.model is None:
            raise FlamaException("Feature model is not defined.")

        name = "Tree relationships"
        _tree_relationships = [str(r) for r in self.model.get_relations()]
        result = self.construct_result(
            name=name,
            doc=self.tree_relationships.__doc__,
            result=_tree_relationships,
            size=len(_tree_relationships),
        )
        return result

    @metric_method
    def root_feature(self) -> dict[str, Any]:
        """The root of the feature model."""
        if self.model is None:
            raise FlamaException("Feature model is not defined.")

        name = "Root feature"
        _root_feature = self.model.root.name
        result = self.construct_result(
            name=name,
            doc=self.root_feature.__doc__,
            result=_root_feature,
            size=1,
            ratio=self.get_ratio([_root_feature], self._features),
        )
        return result

    @metric_method
    def top_features(self) -> dict[str, Any]:
        """Features that are first descendants of the root."""
        if self.model is None:
            raise FlamaException("Feature model is not defined.")

        name = "Top features"
        _top_features = [
            f.name for r in self.model.root.get_relations() for f in r.children
        ]
        result = self.construct_result(
            name=name,
            doc=self.top_features.__doc__,
            result=_top_features,
            size=len(_top_features),
            ratio=self.get_ratio(_top_features, self._features),
        )
        return result

    @metric_method
    def solitary_features(self) -> dict[str, Any]:
        """Features that are not grouped in a feature group."""
        if self.model is None:
            raise FlamaException("Feature model is not defined.")

        name = "Solitary features"
        _solitary_features = [
            f.name
            for f in self._features
            if not f.is_root() and f.parent is not None and not f.parent.is_group()
        ]
        result = self.construct_result(
            name=name,
            doc=self.solitary_features.__doc__,
            result=_solitary_features,
            size=len(_solitary_features),
            ratio=self.get_ratio(_solitary_features, self._features),
        )
        return result

    @metric_method
    def grouped_features(self) -> dict[str, Any]:
        """Features that occurs in a feature group."""
        name = "Grouped features"
        _grouped_features = [
            f.name
            for f in self._features
            if not f.is_root() and f.parent is not None and f.parent.is_group()
        ]
        result = self.construct_result(
            name=name,
            doc=self.grouped_features.__doc__,
            result=_grouped_features,
            size=len(_grouped_features),
            ratio=self.get_ratio(_grouped_features, self._features),
        )
        return result

    @metric_method
    def mandatory_features(self) -> dict[str, Any]:
        """Features marked as mandatory that need to be selected if its parent is selected."""
        if self.model is None:
            raise FlamaException("Feature model is not defined.")

        name = "Mandatory features"
        _mandatory_features = [f.name for f in self.model.get_mandatory_features()]
        result = self.construct_result(
            name=name,
            doc=self.mandatory_features.__doc__,
            result=_mandatory_features,
            size=len(_mandatory_features),
            ratio=self.get_ratio(
                _mandatory_features, self.solitary_features()["result"]
            ),
        )
        return result

    @metric_method
    def optional_features(self) -> dict[str, Any]:
        """Feature marked as optional."""
        if self.model is None:
            raise FlamaException("Feature model is not defined.")

        name = "Optional features"
        _optional_features = [f.name for f in self.model.get_optional_features()]
        result = self.construct_result(
            name=name,
            doc=self.optional_features.__doc__,
            result=_optional_features,
            size=len(_optional_features),
            ratio=self.get_ratio(
                _optional_features, self.solitary_features()["result"]
            ),
        )
        return result

    @metric_method
    def feature_groups(self) -> dict[str, Any]:
        """Features that express a choice over the grouped features in a group."""
        if self.model is None:
            raise FlamaException("Feature model is not defined.")

        name = "Feature groups"
        _tree_relationships = list(self.model.get_relations())
        _feature_groups = [f.name for f in self._features if f.is_group()]
        result = self.construct_result(
            name=name,
            doc=self.feature_groups.__doc__,
            result=_feature_groups,
            size=len(_feature_groups),
            ratio=self.get_ratio(_feature_groups, _tree_relationships),
        )
        return result

    @metric_method
    def alternative_groups(self) -> dict[str, Any]:
        """Feature groups that require the selection of just one child (i.e., [1..1]
        cardinality)."""
        if self.model is None:
            raise FlamaException("Feature model is not defined.")

        name = "Alternative groups"
        _group_features = [f.name for f in self._features if f.is_group()]
        _alternative_groups = [
            f.name for f in self.model.get_alternative_group_features()
        ]
        result = self.construct_result(
            name=name,
            doc=self.alternative_groups.__doc__,
            result=_alternative_groups,
            size=len(_alternative_groups),
            ratio=self.get_ratio(_alternative_groups, _group_features),
        )
        return result

    @metric_method
    def or_groups(self) -> dict[str, Any]:
        """Feature groups that require the selection of at least one child (i.e., [1..*]
        cardinality)."""
        if self.model is None:
            raise FlamaException("Feature model is not defined.")

        name = "Or groups"
        _group_features = [f.name for f in self._features if f.is_group()]
        _or_groups = [f.name for f in self.model.get_or_group_features()]
        result = self.construct_result(
            name=name,
            doc=self.or_groups.__doc__,
            result=_or_groups,
            size=len(_or_groups),
            ratio=self.get_ratio(_or_groups, _group_features),
        )
        return result

    @metric_method
    def mutex_groups(self) -> dict[str, Any]:
        """Feature groups that require the selection of zero or just one child (i.e.,
        [0..1] cardinality)."""
        name = "Mutex groups"
        _group_features = [f.name for f in self._features if f.is_group()]
        _mutex_groups = [f.name for f in self._features if f.is_mutex_group()]
        result = self.construct_result(
            name=name,
            doc=self.mutex_groups.__doc__,
            result=_mutex_groups,
            size=len(_mutex_groups),
            ratio=self.get_ratio(_mutex_groups, _group_features),
        )
        return result

    @metric_method
    def cardinality_groups(self) -> dict[str, Any]:
        """Feature groups with arbitrary cardinality [a..b] that require the selection
        of a minimum and a maximum number of children."""
        name = "Cardinality groups"
        _group_features = [f.name for f in self._features if f.is_group()]
        _cardinality_groups = [
            f.name for f in self._features if f.is_cardinality_group()
        ]
        result = self.construct_result(
            name=name,
            doc=self.cardinality_groups.__doc__,
            result=_cardinality_groups,
            size=len(_cardinality_groups),
            ratio=self.get_ratio(_cardinality_groups, _group_features),
        )
        return result

    @metric_method
    def branching_factor(self) -> dict[str, Any]:
        """Average number of children per non-leaf feature (aka 'Ratio of Variability')."""
        if self.model is None:
            raise FlamaException("Feature model is not defined.")

        name = "Branching factor"
        _avg_branching_factor = fm_operations.average_branching_factor(self.model)
        result = self.construct_result(
            name=name, doc=self.branching_factor.__doc__, result=_avg_branching_factor
        )
        return result

    @metric_method
    def min_children_per_feature(self) -> dict[str, Any]:
        """Minimal number of children per non-leaf feature."""
        name = "Min children per feature"
        _min_children_per_feature = min(
            sum(len(r.children) for r in feature.get_relations())
            for feature in self._features
            if not feature.is_leaf()
        )
        result = self.construct_result(
            name=name,
            doc=self.min_children_per_feature.__doc__,
            result=_min_children_per_feature,
        )
        return result

    @metric_method
    def max_children_per_feature(self) -> dict[str, Any]:
        """Maximal number of children per feature."""
        name = "Max children per feature"
        _max_children_per_feature = max(
            sum(len(r.children) for r in feature.get_relations())
            for feature in self._features
        )
        result = self.construct_result(
            name=name,
            doc=self.max_children_per_feature.__doc__,
            result=_max_children_per_feature,
        )
        return result

    @metric_method
    def avg_children_per_feature(self) -> dict[str, Any]:
        """Average number of children per feature."""
        name = "Avg children per feature"
        nof_children = sum(
            len(r.children)
            for feature in self._features
            for r in feature.get_relations()
        )
        _avg_children_per_feature = round(nof_children / len(self._features), 2)
        result = self.construct_result(
            name=name,
            doc=self.avg_children_per_feature.__doc__,
            result=_avg_children_per_feature,
        )
        return result

    @metric_method
    def depth_tree(self) -> dict[str, Any]:
        """Number of features of the longest path from the root to the leaf features."""
        name = "Depth of tree"
        _max_depth_tree = max(self._feature_ancestors)
        result = self.construct_result(
            name=name, doc=self.depth_tree.__doc__, result=_max_depth_tree
        )
        return result

    @metric_method
    def max_depth_tree(self) -> dict[str, Any]:
        """Number of features of the longest path from the root to the leaf features."""
        name = "Max depth of tree"
        _max_depth_tree = max(self._feature_ancestors)
        result = self.construct_result(
            name=name, doc=self.max_depth_tree.__doc__, result=_max_depth_tree
        )
        return result

    @metric_method
    def mean_depth_tree(self) -> dict[str, Any]:
        """Number of features of the mean path from the root to the leaf features."""
        name = "Mean depth of tree"
        _mean_depth_tree = statistics.mean(self._feature_ancestors)
        result = self.construct_result(
            name=name,
            doc=self.mean_depth_tree.__doc__,
            result=round(_mean_depth_tree, 2),
        )
        return result

    @metric_method
    def median_depth_tree(self) -> dict[str, Any]:
        """Number of features of the median path from the root to the leaf features."""
        name = "Median depth of tree"
        _median_depth_tree = statistics.median(self._feature_ancestors)
        result = self.construct_result(
            name=name,
            doc=self.median_depth_tree.__doc__,
            result=round(_median_depth_tree, 2),
        )
        return result

    @metric_method
    def cross_tree_constraints(self) -> dict[str, Any]:
        """Textual cross-tree constraints."""
        if self.model is None:
            raise FlamaException("Feature model is not defined.")

        name = "Cross-tree constraints"
        _cross_tree_constraints = [str(ctc) for ctc in self.model.get_constraints()]
        result = self.construct_result(
            name=name,
            doc=self.cross_tree_constraints.__doc__,
            result=_cross_tree_constraints,
            size=len(_cross_tree_constraints),
        )
        return result

    @metric_method
    def simple_constraints(self) -> dict[str, Any]:
        """Requires and Excludes constraints."""
        if self.model is None:
            raise FlamaException("Feature model is not defined.")

        name = "Simple constraints"
        _simple_constraints = [str(ctc) for ctc in self.model.get_simple_constraints()]
        result = self.construct_result(
            name=name,
            doc=self.simple_constraints.__doc__,
            result=_simple_constraints,
            size=len(_simple_constraints),
            ratio=self.get_ratio(_simple_constraints, self.model.get_constraints()),
        )
        return result

    @metric_method
    def requires_constraints(self) -> dict[str, Any]:
        """Constraints modeling that the activation of a feature f1 implies the
        activation of a feature f2."""
        if self.model is None:
            raise FlamaException("Feature model is not defined.")

        name = "Requires constraints"
        _requires_constraints = [
            str(ctc) for ctc in self.model.get_requires_constraints()
        ]
        result = self.construct_result(
            name=name,
            doc=self.requires_constraints.__doc__,
            result=_requires_constraints,
            size=len(_requires_constraints),
            ratio=self.get_ratio(
                _requires_constraints, self.model.get_simple_constraints()
            ),
        )
        return result

    @metric_method
    def excludes_constraints(self) -> dict[str, Any]:
        """Constraints modeling that two features are mutually exclusive and cannot be
        activated together."""
        if self.model is None:
            raise FlamaException("Feature model is not defined.")

        name = "Excludes constraints"
        _excludes_constraints = [
            str(ctc) for ctc in self.model.get_excludes_constraints()
        ]
        result = self.construct_result(
            name=name,
            doc=self.excludes_constraints.__doc__,
            result=_excludes_constraints,
            size=len(_excludes_constraints),
            ratio=self.get_ratio(
                _excludes_constraints, self.model.get_simple_constraints()
            ),
        )
        return result

    @metric_method
    def complex_constraints(self) -> dict[str, Any]:
        """Constraints in arbitrary propositional logic formulae."""
        if self.model is None:
            raise FlamaException("Feature model is not defined.")

        name = "Complex constraints"
        _complex_constraints = [
            str(ctc) for ctc in self.model.get_complex_constraints()
        ]
        result = self.construct_result(
            name=name,
            doc=self.complex_constraints.__doc__,
            result=_complex_constraints,
            size=len(_complex_constraints),
            ratio=self.get_ratio(_complex_constraints, self.model.get_constraints()),
        )
        return result

    @metric_method
    def pseudo_complex_constraints(self) -> dict[str, Any]:
        """Constraints that are convertible to a set of simple constraints."""
        if self.model is None:
            raise FlamaException("Feature model is not defined.")

        name = "Pseudo-complex constraints"
        _pseudocomplex_constraints = [
            str(ctc) for ctc in self.model.get_pseudocomplex_constraints()
        ]
        result = self.construct_result(
            name=name,
            doc=self.pseudo_complex_constraints.__doc__,
            result=_pseudocomplex_constraints,
            size=len(_pseudocomplex_constraints),
            ratio=self.get_ratio(
                _pseudocomplex_constraints, self.model.get_complex_constraints()
            ),
        )
        return result

    @metric_method
    def strict_complex_constraints(self) -> dict[str, Any]:
        """Constraints that cannot be converted to a set of simple constraints."""
        if self.model is None:
            raise FlamaException("Feature model is not defined.")

        name = "Strict-complex constraints"
        _strictcomplex_constraints = [
            str(ctc) for ctc in self.model.get_strictcomplex_constraints()
        ]
        result = self.construct_result(
            name=name,
            doc=self.strict_complex_constraints.__doc__,
            result=_strictcomplex_constraints,
            size=len(_strictcomplex_constraints),
            ratio=self.get_ratio(
                _strictcomplex_constraints, self.model.get_complex_constraints()
            ),
        )
        return result

    @metric_method
    def min_constraints_per_feature(self) -> dict[str, Any]:
        """The minimal number of constraints per feature."""
        name = "Min constraints per feature"
        _constraints_per_feature = self._constraints_per_features
        result = self.construct_result(
            name=name,
            doc=self.min_constraints_per_feature.__doc__,
            result=min(_constraints_per_feature),
        )
        return result

    @metric_method
    def max_constraints_per_feature(self) -> dict[str, Any]:
        """The maximal number of constraints per feature."""
        name = "Max constraints per feature"
        _constraints_per_feature = self._constraints_per_features
        result = self.construct_result(
            name=name,
            doc=self.max_constraints_per_feature.__doc__,
            result=max(_constraints_per_feature),
        )
        return result

    @metric_method
    def avg_constraints_per_feature(self) -> dict[str, Any]:
        """The average number of constraints per feature."""
        name = "Avg constraints per feature"
        _constraints_per_feature = self._constraints_per_features
        result = self.construct_result(
            name=name,
            doc=self.avg_constraints_per_feature.__doc__,
            result=round(statistics.mean(_constraints_per_feature), 2),
        )
        return result

    @metric_method
    def extra_constraint_representativeness(self) -> dict[str, Any]:
        """Features involved in cross-tree constraints. The ratio to the total number of
        features is called 'Extra constraint representativeness (ECR)'."""
        if self.model is None:
            raise FlamaException("Feature model is not defined.")

        name = "Features in constraints"
        _features_in_constraints = list(
            {f for ctc in self.model.get_constraints() for f in ctc.get_features()}
        )
        result = self.construct_result(
            name=name,
            doc=self.extra_constraint_representativeness.__doc__,
            result=_features_in_constraints,
            size=len(_features_in_constraints),
            ratio=self.get_ratio(_features_in_constraints, self._features, 2),
        )
        return result
