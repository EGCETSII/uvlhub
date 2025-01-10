from abc import abstractmethod
from typing import Any

from flamapy.core.operations import Operation


class ProductDistribution(Operation):
    """The Product Distribution (PD) operation determines the number of products 
    having a given number of features.

    It accounts for how many products have no features, one features, 
    two features, ..., all features.

    This operation also provides a descriptive statistics summarizing the product distribution of 
    a variability model. Concretely, it provides:
    Mean, Standard deviation, Median, Median absolute deviation, Mode, Min, Max, and Range, of the
    product distribution of the variability model.

    This operation in combination with the Feature Inclusion Probability (FIP) operation
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
    def product_distribution(self) -> list[int]:
        pass

    @abstractmethod
    def descriptive_statistics(self) -> dict[str, Any]:
        pass
