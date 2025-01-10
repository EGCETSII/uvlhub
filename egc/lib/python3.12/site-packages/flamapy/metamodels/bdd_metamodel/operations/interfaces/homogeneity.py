from abc import abstractmethod

from flamapy.core.operations import Operation


class Homogeneity(Operation):
    """The homogeneity of an SPL is the commonality mean, i.e., the sum of the commonality factor 
    of all the features in the SPL divided by the number of features.

    The commonality factor of a single feature f is the commonality factor of a configuration with 
    the single feature f as selected and no removed features,

    Ref.: [Duran et al. 2017. FLAME: a formal framework for the automated analysis of software 
    product lines validated by automated specification testing. 
    (https://doi.org/10.1007/s10270-015-0503-z)]
    """

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def homogeneity(self) -> float:
        pass
