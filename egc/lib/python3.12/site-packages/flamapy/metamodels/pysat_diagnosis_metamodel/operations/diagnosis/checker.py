"""
A Java version of this implementation is available at:
https://github.com/HiConfiT/hiconfit-core/blob/main/ca-cdr-package/src/main/java/at/tugraz/ist/ase/cacdr/checker/ChocoConsistencyChecker.java
"""
from typing import List

from pysat.solvers import Solver


class ConsistencyChecker:
  
    def __init__(self, solver_name: str, set_kb: List[List[int]]) -> None:
        self.result = False

        self.solver = Solver(solver_name, bootstrap_with=set_kb)

    def is_consistent(self, set_c: List[int], delta: List[int]) -> bool:
        """
        Check if the given CNF formula is consistent using a solver.
        :param set_c: a list of assumptions should be added to the CNF formula
        :param delta: a list of assumptions should not be added to the CNF formula
        :return: a boolean value indicating whether the given CNF formula is consistent
        """
        assumptions = set_c + [-1 * item for item in delta]
        self.result = self.solver.solve(assumptions=assumptions)
        # print(f"assumptions: {assumptions} - result: {self.result}")
        return self.result

    def delete(self) -> None:
        self.solver.delete()