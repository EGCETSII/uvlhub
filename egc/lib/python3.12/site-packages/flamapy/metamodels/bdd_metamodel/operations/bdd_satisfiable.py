from typing import cast

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Satisfiable
from flamapy.metamodels.bdd_metamodel.models import BDDModel


class BDDSatisfiable(Satisfiable):
    """Checks if the BDD is not equal to its false terminal node to determine satisfiability. 

    If the BDD is not equal to the false node, it means there exists at least one valid assignment 
    of variables that satisfies the formula, indicating that the formula is satisfiable. 
    Otherwise, if the BDD is equal to the false node, it means no valid assignment of variables 
    satisfies the formula, indicating that the formula is not satisfiable.
    """

    def __init__(self) -> None:
        self._result: bool = False

    def get_result(self) -> bool:
        return self._result

    def is_satisfiable(self) -> bool:
        return self.get_result()

    def execute(self, model: VariabilityModel) -> 'BDDSatisfiable':
        bdd_model = cast(BDDModel, model)
        self._result = is_satisfiable(bdd_model)
        return self


def is_satisfiable(bdd_model: BDDModel) -> bool:
    return not bdd_model.is_terminal_n0(bdd_model.root)
