from abc import abstractmethod
from typing import Any

from flamapy.core.operations import Operation


class UniqueFeatures(Operation):
    """Unique features are those that appear in only one configuration.

    Ref.: [Duran et al. 2017. FLAME: a formal framework for the automated analysis of software 
    product lines validated by automated specification testing. 
    (https://doi.org/10.1007/s10270-015-0503-z)]
    """

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def unique_features(self) -> list[Any]:
        pass
