from typing import Any, cast, Callable, Optional

from flamapy.core.models import VariabilityModel
from flamapy.core.exceptions import FlamaException
from flamapy.core.operations.metrics_operation import Metrics
from flamapy.metamodels.bdd_metamodel.models import BDDModel
from flamapy.metamodels.bdd_metamodel import operations as bdd_operations


def metric_method(func: Callable) -> Callable:
    """Decorator to mark a method as a metric method.
    It has the value of the measure, it can also have a size and a ratio.
    Example:
        property name: Abstract Features.
        description: The description of the property.
        value (optional): the list of abstract features.
        size (optional): the length of the list.
        ratio (optional): the percentage of abstract features with regards the total number
                            of features.
    """
    if not hasattr(func, '_is_metric_method'):
        setattr(func, '_is_metric_method', True)
    return func


class BDDMetrics(Metrics):

    def __init__(self) -> None:
        super().__init__()
        self.model: Optional[VariabilityModel] = None
        self.result: list[dict[str, Any]] = []
        self.model_type_extension = "bdd"
        self._features: list[Any] = []
        self._configurations_number: int = 0
        self._fip: dict[Any, float] = {}
        self._prod_dist: list[int] = []
        self._prod_dist_op: bdd_operations.BDDProductDistribution = None
        self._variant_features: list[Any] = []

    def get_result(self) -> list[dict[str, Any]]:
        return self.result

    def calculate_metamodel_metrics(self, model: VariabilityModel) -> list[dict[str, Any]]:
        self.model = cast(BDDModel, model)

        #Do some basic calculations to speedup the rest
        self._features = self.model.variables
        self._configurations_number = bdd_operations.BDDConfigurationsNumber() \
                                      .execute(self.model).get_result()
        self._prod_dist_op = bdd_operations.BDDProductDistribution()
        self._prod_dist = self._prod_dist_op.execute(self.model).get_result()
        self._fip = bdd_operations.BDDFeatureInclusionProbability() \
                    .execute(self.model).get_result()
        self._variant_features = [feat for feat, prob, in self._fip.items() if 0.0 < prob < 1.0]
        # Get all methods that are marked with the metric_method decorator
        metric_methods = [getattr(self, method_name) for method_name in dir(self)
                          if callable(getattr(self, method_name)) and 
                          hasattr(getattr(self, method_name), '_is_metric_method')]
        if self.filter is not None:
            metric_methods = [method for method in metric_methods 
                              if method.__name__ in self.filter]

        return [method() for method in metric_methods]

    @metric_method
    def satisfiable(self) -> dict[str, Any]:
        """A feature model is satisfiable if it represents at least one configuration."""
        if self.model is None:
            raise FlamaException('Model not initialized.')
        name = "satisfiable (valid) (not void)"
        _satisfiable = bdd_operations.BDDSatisfiable().execute(self.model).get_result()
        return self.construct_result(name=name, doc=self.satisfiable.__doc__, result=_satisfiable)

    @metric_method
    def core_features(self) -> dict[str, Any]:
        """Features that are part of all the configurations (a.k.a., 'common features')."""
        name = "Core features"
        _core = [feat for feat, prob, in self._fip.items() if prob >= 1.0]
        return self.construct_result(name=name,
                                     doc=self.core_features.__doc__,
                                     result=_core,
                                     size=len(_core),
                                     ratio=self.get_ratio(_core, self._features, 2))

    @metric_method
    def dead_features(self) -> dict[str, Any]:
        """Features that cannot appear in any configuration."""
        if self.model is None:
            raise FlamaException('Model not initialized.')
        name = "Dead features"
        _dead_features = [feat for feat, prob, in self._fip.items() if prob <= 0.0]
        return self.construct_result(name=name,
                                     doc=self.dead_features.__doc__,
                                     result=_dead_features,
                                     size=len(_dead_features),
                                     ratio=self.get_ratio(_dead_features, self._features, 2))
    
    @metric_method
    def pure_optional_features(self) -> dict[str, Any]:
        """Pure optional features are those feature with 0.5 (50%) probability of being selected 
        in a valid configuration, that is, their selection is unconstrained."""
        if self.model is None:
            raise FlamaException('Model not initialized.')
        name = "Pure optional features"
        _pure_optional_features = [feat for feat, prob, in self._fip.items() if prob == 0.5]
        return self.construct_result(name=name,
                                     doc=self.pure_optional_features.__doc__,
                                     result=_pure_optional_features,
                                     size=len(_pure_optional_features),
                                     ratio=self.get_ratio(_pure_optional_features, 
                                                          self._features, 2))

    @metric_method
    def variant_features(self) -> dict[str, Any]:
        """The variant features of an SPL are those features that appear only in some 
        configurations of the SPL, i.e., the features that are neither core features nor dead 
        features."""
        if self.model is None:
            raise FlamaException('Model not initialized.')
        name = "Variant features"
        _variant_features = self._variant_features
        return self.construct_result(name=name,
                                     doc=self.variant_features.__doc__,
                                     result=_variant_features,
                                     size=len(_variant_features),
                                     ratio=self.get_ratio(_variant_features, 
                                                          self._features, 2))

    @metric_method
    def unique_features(self) -> dict[str, Any]:
        """Unique features are those that appear in only one configuration."""
        if self.model is None:
            raise FlamaException('Model not initialized.')
        name = "Unique features"
        _unique_features = bdd_operations.BDDUniqueFeatures().execute(self.model).get_result()
        return self.construct_result(name=name,
                                     doc=self.unique_features.__doc__,
                                     result=_unique_features,
                                     size=len(_unique_features),
                                     ratio=self.get_ratio(_unique_features, 
                                                          self._features, 2))
    
    @metric_method
    def total_variability(self) -> dict[str, Any]:
        """The total variability of an SPL, considered as a measure of its flexibility, is the 
        ratio between the number of its valid configurations and the number of the potential 
        configurations it could have, i.e., 2^n-1 where n is the number of all the SPL features."""
        if self.model is None:
            raise FlamaException('Model not initialized.')
        name = "Total variability"
        _total_variability = self.configurations_number / (2**len(self._features) - 1)
        return self.construct_result(name=name,
                                     doc=self.total_variability.__doc__,
                                     result=_total_variability)

    @metric_method
    def partial_variability(self) -> dict[str, Any]:
        """The partial variability of an SPL, considered as a measure of its flexibility, is the 
        ratio between the number of its valid configurations and the number of potential 
        configurations it could have, i.e., 2^n-1 where n is the number of variant features."""
        if self.model is None:
            raise FlamaException('Model not initialized.')
        name = "Partial variability"
        _partial_variability = self.configurations_number / (2**len(self._variant_features) - 1)
        return self.construct_result(name=name,
                                     doc=self.partial_variability.__doc__,
                                     result=_partial_variability)
    
    @metric_method
    def homogeneity(self) -> dict[str, Any]:
        """The homogeneity of an SPL is the commonality mean, i.e., the sum of the commonality 
        factor of all the features in the SPL divided by the number of features."""
        if self.model is None:
            raise FlamaException('Model not initialized.')
        name = "Homogeneity"
        _homogeneity = bdd_operations.BDDHomogeneity().execute(self.model).get_result()
        return self.construct_result(name=name,
                                     doc=self.homogeneity.__doc__,
                                     result=_homogeneity)
    
    @metric_method
    def configurations(self) -> dict[str, Any]:
        """Configurations represented by the feature model."""
        if self.model is None:
            raise FlamaException('Model not initialized.')
        name = "Configurations"
        _configurations = bdd_operations.BDDConfigurations().execute(self.model).get_result()
        return self.construct_result(name=name,
                                     doc=self.configurations.__doc__,
                                     result=_configurations,
                                     size=len(_configurations))

    @metric_method
    def configurations_number(self) -> dict[str, Any]:
        """Number of valid configurations represented by the feature model."""
        if self.model is None:
            raise FlamaException('Model not initialized.')
        name = "Configurations number"
        _configurations_number = self._configurations_number
        return self.construct_result(name=name,
                                     doc=self.configurations_number.__doc__,
                                     result=_configurations_number)

    @metric_method
    def product_distribution(self) -> dict[str, Any]:
        """The Product Distribution determines the number of configurations having a given number 
        of features."""
        if self.model is None:
            raise FlamaException('Model not initialized.')
        name = "Product distribution"
        _dist = self._prod_dist
        return self.construct_result(name=name,
                                     doc=self.product_distribution.__doc__,
                                     result=_dist)

    @metric_method
    def descriptive_statistics(self) -> dict[str, Any]:
        """The descriptive statistics summarizes the product distribution of a variability model. 
        Concretely, it provides: Mean, Standard deviation, Median, Median absolute deviation, Mode, 
        Min, Max, and Range, of the product distribution of the variability model."""
        if self.model is None:
            raise FlamaException('Model not initialized.')
        name = "Descriptive statistics"
        _desc_stats = self._prod_dist_op.descriptive_statistics()
        return self.construct_result(name=name,
                                     doc=self.descriptive_statistics.__doc__,
                                     result=_desc_stats)

    @metric_method
    def feature_inclusion_probabilities(self) -> dict[str, Any]:
        """The Feature Inclusion Probability determines the probability for a feature to be 
        included in a valid configuration."""
        if self.model is None:
            raise FlamaException('Model not initialized.')
        name = "Feature inclusion probabilities"
        _prob = self._fip
        return self.construct_result(name=name,
                                     doc=self.feature_inclusion_probabilities.__doc__,
                                     result=_prob)
