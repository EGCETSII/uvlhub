from typing import Tuple

from flamapy.metamodels.pysat_diagnosis_metamodel.models import DiagnosisModel
from . import PySATAbstractIdentifier
from .diagnosis.checker import ConsistencyChecker
from .diagnosis.hsdag.hsdag import HSDAG
from .diagnosis.hsdag.labeler.fastdiag_labeler import FastDiagParameters, FastDiagLabeler


class PySATDiagnosis(PySATAbstractIdentifier):
    """
    An operation that computes diagnoses and conflict sets
    using the combination of HSDAG and FastDiag algorithms.
    Four optional inputs:
    - configuration - a configuration to be diagnosed
    - test_case - a test case to be used for diagnosis
    - max_diagnoses - specify the maximum number of diagnoses to be computed
    - max_depth - specify the maximum depth of the HSDAG to be computed
    """

    def __init__(self) -> None:
        super().__init__()
        self.max_diagnoses = -1  # -1 means no limit

    def set_max_diagnoses(self, max_diagnoses: int) -> None:
        self.max_diagnoses = max_diagnoses

    def prepare_hsdag(self, model: DiagnosisModel) -> Tuple[ConsistencyChecker, HSDAG]:
        # transform model to diagnosis model
        model.prepare_diagnosis_task(configuration=self.configuration, test_case=self.test_case)

        set_c = model.get_c()

        checker = ConsistencyChecker(self.solver_name, model.get_kb())
        parameters = FastDiagParameters(set_c, [], model.get_b())
        labeler = FastDiagLabeler(checker, parameters)

        hsdag = HSDAG(labeler)
        hsdag.max_number_diagnoses = self.max_diagnoses
        hsdag.max_depth = self.max_depth

        return checker, hsdag

    def set_result_messages(self, cs_mess: str, diag_mess: str) -> None:
        self.result_messages.append(diag_mess)
        self.result_messages.append(cs_mess)
