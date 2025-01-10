from abc import abstractmethod

from flamapy.core.operations import Operation
from flamapy.metamodels.configuration_metamodel.models import Configuration


class CommonalityFactor(Operation):
    """The commonality factor of a configuration in an SPL is the percentage of products 
    of the SPL including the given configuration (0 if the SPL is void).

    Ref.: [Duran et al. 2017. FLAME: a formal framework for the automated analysis of software 
    product lines validated by automated specification testing. 
    (https://doi.org/10.1007/s10270-015-0503-z)]
    """

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def set_configuration(self, configuration: Configuration) -> None:
        pass

    @abstractmethod
    def commonality_factor(self) -> float:
        pass
