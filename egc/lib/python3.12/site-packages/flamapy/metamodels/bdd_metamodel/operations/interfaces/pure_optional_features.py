from abc import abstractmethod
from typing import Any

from flamapy.core.operations import Operation


class PureOptionalFeatures(Operation):
    """Pure optional features are those feature with 0.5 (50%) probability 
    of being selected in a valid configuration, that is, their selection is unconstrained.

    Ref.: [Heradio et al. 2019. Supporting the Statistical Analysis of Variability Models. 
    (https://doi.org/10.1109/ICSE.2019.00091)]
    """

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def pure_optional_features(self) -> list[Any]:
        pass
