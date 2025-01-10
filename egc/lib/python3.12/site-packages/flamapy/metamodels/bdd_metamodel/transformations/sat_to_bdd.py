from typing import Optional

from flamapy.core.transformations import ModelToModel
from flamapy.metamodels.bdd_metamodel.models import BDDModel
from flamapy.metamodels.pysat_metamodel.models import PySATModel


class SATToBDD(ModelToModel):

    @staticmethod
    def get_source_extension() -> str:
        return "pysat"

    @staticmethod
    def get_destination_extension() -> str:
        return "bdd"

    def __init__(self, source_model: PySATModel) -> None:
        self.source_model = source_model
        self.destination_model: Optional[BDDModel] = None

    def transform(self) -> BDDModel:
        # Transform clauses to textual CNF notation required by the BDD
        not_connective = BDDModel.NOT
        or_connective = " " + BDDModel.OR + " "
        and_connective = " " + BDDModel.AND + " "
        cnf_list = []
        for clause in self.source_model.get_all_clauses().clauses:
            cnf_list.append(
                "("
                + or_connective.join(
                    list(
                        map(
                            lambda elem: not_connective
                            + self.source_model.features[abs(elem)]
                            if elem < 0
                            else self.source_model.features[abs(elem)],
                            clause,
                        )
                    )
                )
                + ")"
            )
        cnf_formula = and_connective.join(cnf_list)
        bdd_model = BDDModel.from_textual_cnf(cnf_formula, 
                                              list(self.source_model.variables.keys()))
        self.destination_model = bdd_model
        return self.destination_model
