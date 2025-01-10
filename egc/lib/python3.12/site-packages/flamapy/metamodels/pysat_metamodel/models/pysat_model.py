from pysat.formula import CNF

from flamapy.core.exceptions import FlamaException
from flamapy.core.models import VariabilityModel


class PySATModel(VariabilityModel):
    @staticmethod
    def get_extension() -> str:
        return 'pysat'

    def __init__(self) -> None:
        self._cnf = CNF()
        self.variables: dict[str, int] = {}  # feature's name -> id
        self.features: dict[int, str] = {}  # id -> feature's name
        self.original_model: VariabilityModel

    def add_clause(self, clause: list[int]) -> None:
        self._cnf.append(clause)

    def get_variable(self, key: str) -> int:
        if key not in self.variables:
            raise FlamaException(f'Feature {key} not found')
        return self.variables[key]

    def get_all_clauses(self) -> CNF:
        return self._cnf
