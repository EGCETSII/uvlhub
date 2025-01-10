from abc import abstractmethod
from typing import cast, List, Tuple

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Operation
from flamapy.metamodels.configuration_metamodel.models import Configuration

from .diagnosis.checker import ConsistencyChecker
from .diagnosis.hsdag.hsdag import HSDAG
from ..models.pysat_diagnosis_model import DiagnosisModel


def _execute_hsdag(model: DiagnosisModel, hsdag: HSDAG) -> Tuple[str, str]:
    hsdag.construct()
    diagnoses = hsdag.get_diagnoses()
    conflicts = hsdag.get_conflicts()

    if len(diagnoses) == 0:
        diag_mess = 'No diagnosis found'
    elif len(diagnoses) == 1:
        diag_mess = 'Diagnosis: '
        diag_mess += model.get_pretty_diagnoses(diagnoses)
    else:
        diag_mess = 'Diagnoses: '
        diag_mess += model.get_pretty_diagnoses(diagnoses)
    if len(conflicts) == 0:
        cs_mess = 'No conflicts found'
    elif len(conflicts) == 1:
        cs_mess = 'Conflict: '
        cs_mess += model.get_pretty_diagnoses(conflicts)
    else:
        cs_mess = 'Conflicts: '
        cs_mess += model.get_pretty_diagnoses(conflicts)

    return cs_mess, diag_mess


class PySATAbstractIdentifier(Operation):
    """
    An abstract operation for computes conflicts or diagnoses.
    Four optional inputs:
    - configuration - a configuration to be diagnosed
    - test_case - a test case to be used for diagnosis
    - max_depth - specify the maximum depth of the HSDAG to be computed
    """

    def __init__(self) -> None:
        self.result = False
        self.configuration = None
        self.test_case = None
        self.solver_name = 'glucose3'
        self.result_messages: List[str] = []

        self.checker = None
        self.max_depth = 0  # 0 means no limit

    def set_max_depth(self, max_depth: int) -> None:
        self.max_depth = max_depth

    def set_configuration(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def set_test_case(self, test_case: Configuration) -> None:
        self.test_case = test_case

    def get_result(self) -> List[str]:
        return self.result_messages

    def execute(self, model: VariabilityModel) -> 'PySATAbstractIdentifier':
        model = cast(DiagnosisModel, model)

        checker, labeler = self.prepare_hsdag(model)

        cs_mess, diag_mess = _execute_hsdag(model, labeler)

        self.set_result_messages(cs_mess, diag_mess)
        checker.delete()
        return self

    @abstractmethod
    def prepare_hsdag(self, model: DiagnosisModel) -> Tuple[ConsistencyChecker, HSDAG]:
        pass

    @abstractmethod
    def set_result_messages(self, cs_mess: str, diag_mess: str) -> None:
        pass