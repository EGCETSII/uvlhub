from abc import abstractmethod
from typing import Any

from flamapy.core.operations import Operation


class FeatureInclusionProbability(Operation):
    """The Feature Inclusion Probability (FIP) operation determines the probability 
    for a feature to be included in a valid product. 

    It obtains, for each feature, the proportion of valid products that include it.

    This operation in combination with the Product Distribution (PD) operation
    provides a clear picture of the products' homogeneity (i.e., how much does one product 
    differ from the others).
    The product's homogeneity is one the three core metrics that characterize 
    the complexity of a SPL.
    The other two core metrics are the number of features the SPL manages, 
    and the number of valid product that can be derived.

    Ref.: [Heradio et al. 2019. Supporting the Statistical Analysis of Variability Models. 
    (https://doi.org/10.1109/ICSE.2019.00091)]
    """

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def feature_inclusion_probability(self) -> dict[Any, float]:
        pass
