from typing import Optional

from flamapy.core.exceptions import FlamaException
from flamapy.core.transformations import TextToModel
from flamapy.metamodels.pysat_metamodel.models import PySATModel


class DimacsReader(TextToModel):

    @staticmethod
    def get_source_extension() -> str:
        return 'dimacs'

    def __init__(self, path: str) -> None:
        self.path = path

    def transform(self) -> PySATModel:
        with open(self.path, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()
            problem: Optional[str] = None
            features_lines = []
            clauses_lines = []
            for line in lines:
                if line.startswith('c'):
                    features_lines.append(line)
                elif line.startswith('p'):
                    problem = line
                elif line != '':
                    clauses_lines.append(line)
            if problem is None:
                raise FlamaException(f'Incorrect Dimacs format of {self.path}. '
                                     f'No problem statement.')

            problem_list = problem.split()
            n_clauses = int(problem_list[3])
            if n_clauses != len(clauses_lines):
                raise FlamaException(f'Incorrect Dimacs format of {self.path}. '
                                     f'Inconsistent number of clauses.')
        features, variables = self._parse_features_variables(features_lines)
        sat_model = PySATModel()
        sat_model.features = features
        sat_model.variables = variables
        self._parse_clauses(sat_model, clauses_lines)
        return sat_model

    def _parse_features_variables(self, lines: list[str]) -> tuple[dict[int, str], dict[str, int]]:
        features: dict[int, str] = {}
        variables: dict[str, int] = {}
        for line in lines:
            line_list = line.split()
            var = int(line_list[1])
            feature = line_list[2]
            features[var] = feature
            variables[feature] = var
        return (features, variables)

    def _parse_clauses(self, sat_model: PySATModel, lines: list[str]) -> None:
        for line in lines:
            clause = line.split()
            sat_model.add_clause([int(c) for c in clause if c != '0'])
