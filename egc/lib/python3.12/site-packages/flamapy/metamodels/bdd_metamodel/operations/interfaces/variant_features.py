from abc import abstractmethod
from typing import Any

from flamapy.core.operations import Operation


class VariantFeatures(Operation):
    """The variant features of an SPL are those features that appear only in some products of the 
    SPL, i.e., the features that are neither core features nor dead features, something that can be
    easily expressed by means of the set difference between the SPL features and its core and dead 
    features.

    Ref.: [Duran et al. 2017. FLAME: a formal framework for the automated analysis of software 
    product lines validated by automated specification testing. 
    (https://doi.org/10.1007/s10270-015-0503-z)]
    """

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def variant_features(self) -> list[Any]:
        pass
