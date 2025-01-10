from abc import abstractmethod

from flamapy.core.operations import Operation


class Variability(Operation):
    """The variability of an SPL, considered as a measure of its flexibility.

    It is defined as the ratio between the number of its valid configurations and the number of the 
    potential configurations it could have, i.e., 2^n-1 where n is the number of features under 
    consideration. 
    If all the SPL features are considered, the variability is referred to as total variability (V)
    whereas if only variant features are considered, it is referred to as partial variability (Vρ), 
    which is 0 in case the SPL has no variant features, i.e., in the case the SPL is void or has 
    only one valid configuration.

    Ref.: [Duran et al. 2017. FLAME: a formal framework for the automated analysis of software 
    product lines validated by automated specification testing. 
    (https://doi.org/10.1007/s10270-015-0503-z)]
    """

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def total_variability(self) -> float:
        pass

    @abstractmethod
    def partial_variability(self) -> float:
        pass
