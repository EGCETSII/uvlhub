import itertools
from typing import Optional, Any

from flamapy.core.transformations import ModelToModel
from flamapy.metamodels.fm_metamodel.models import (
    FeatureModel,
    Constraint,
    Feature,
    Relation,
)
from flamapy.metamodels.bdd_metamodel.models import BDDModel


class FmToBDD(ModelToModel):

    @staticmethod
    def get_source_extension() -> str:
        return "fm"

    @staticmethod
    def get_destination_extension() -> str:
        return "bdd"

    def __init__(self, source_model: FeatureModel) -> None:
        self.source_model = source_model
        self.counter = 1
        self.destination_model: Optional[BDDModel] = None
        self.variables: dict[str, int] = {}
        self.features: dict[int, str] = {}
        self.clauses: list[list[int]] = []

    def _get_variable(self, name: str) -> int:
        variable = self.variables.get(name)
        if variable is None:
            raise ValueError("the parent variable wasn't found")
        return variable

    def add_feature(self, feature: Feature) -> None:
        if feature.name not in self.variables:
            self.variables[feature.name] = self.counter
            self.features[self.counter] = feature.name
            self.counter += 1

    def add_root(self, feature: Feature) -> None:
        self.clauses.append([self._get_variable(feature.name)])

    def _add_mandatory_relation(self, relation: Relation) -> list[list[int]]:
        value_parent = self._get_variable(relation.parent.name)
        value_child = self._get_variable(relation.children[0].name)
        clauses = [[-1 * value_parent, value_child], [-1 * value_child, value_parent]]
        return clauses

    def _add_optional_relation(self, relation: Relation) -> list[list[int]]:
        value_parent = self._get_variable(relation.parent.name)
        value_children = self._get_variable(relation.children[0].name)
        clauses = [[-1 * value_children, value_parent]]
        return clauses

    def _add_or_relation(self, relation: Relation) -> list[list[int]]:
        # this is a 1 to n relatinship with multiple childs
        # add the first cnf child1 or child2 or ... or childN or no parent)
        # first elem of the constraint
        value_parent = self._get_variable(relation.parent.name)

        alt_cnf = [-1 * value_parent]
        for child in relation.children:
            alt_cnf.append(self._get_variable(child.name))
        clauses = [alt_cnf]

        for child in relation.children:
            clauses.append([
                -1 * self._get_variable(child.name),
                value_parent
            ])

        return clauses

    def _add_alternative_relation(self, relation: Relation) -> list[list[int]]:
        # this is a 1 to 1 relatinship with multiple childs
        # add the first cnf child1 or child2 or ... or childN or no parent)

        value_parent = self._get_variable(relation.parent.name)
        # first elem of the constraint
        alt_cnf = [-1 * value_parent]
        for child in relation.children:
            alt_cnf.append(self._get_variable(child.name))
        clauses = [alt_cnf]

        for i, _ in enumerate(relation.children):
            for j in range(i + 1, len(relation.children)):
                if i != j:
                    clauses.append([
                        -1 * self._get_variable(relation.children[i].name),
                        -1 * self._get_variable(relation.children[j].name)
                    ])
            clauses.append([
                -1 * self._get_variable(relation.children[i].name),
                value_parent
            ])
        return clauses

    def _add_constraint_relation(self, relation: Relation) -> list[list[int]]:
        value_parent = self._get_variable(relation.parent.name)

        # This is a _min to _max relationship
        _min = relation.card_min
        _max = relation.card_max

        clauses = []

        for val in range(len(relation.children) + 1):
            if val < _min or val > _max:
                # combinations of val elements
                for combination in itertools.combinations(relation.children, val):
                    cnf = [-1 * value_parent]
                    for feat in relation.children:
                        if feat in combination:
                            cnf.append(-1 * self._get_variable(feat.name))
                        else:
                            cnf.append(self._get_variable(feat.name))
                    clauses.append(cnf)

        # there is a special case when coping with the upper part of the thru table
        # In the case of allowing 0 childs, you cannot exclude the option  in that
        # no feature in this relation is activated
        for val in range(1, len(relation.children) + 1):

            for combination in itertools.combinations(relation.children, val):
                cnf = [value_parent]
                for feat in relation.children:
                    if feat in combination:
                        cnf.append(-1 * self._get_variable(feat.name))
                    else:
                        cnf.append(self._get_variable(feat.name))
                clauses.append(cnf)
        return clauses

    def add_relation(self, relation: Relation) -> None:
        if relation.is_mandatory():
            clauses = self._add_mandatory_relation(relation)
        elif relation.is_optional():
            clauses = self._add_optional_relation(relation)
        elif relation.is_or():  
            clauses = self._add_or_relation(relation)
        elif relation.is_alternative():  
            clauses = self._add_alternative_relation(relation)
        else:
            clauses = self._add_constraint_relation(relation)
        self._store_constraint_clauses(clauses)

    def _store_constraint_clauses(self, clauses: list[list[int]]) -> None:
        for clause in clauses:
            self.clauses.append(clause)

    def add_constraint(self, ctc: Constraint) -> None:
        def get_term_variable(term: Any) -> int:
            if term.startswith('-'):
                return -self._get_variable(term[1:])

            return self._get_variable(term)

        clauses = ctc.ast.get_clauses()
        for clause in clauses:
            clause_variables = list(map(get_term_variable, clause))
            self.clauses.append(clause_variables)

    def transform(self) -> BDDModel:
        for feature in self.source_model.get_features():
            self.add_feature(feature)

        self.add_root(self.source_model.root)

        for relation in self.source_model.get_relations():
            self.add_relation(relation)

        for constraint in self.source_model.get_constraints():
            self.add_constraint(constraint)

        # Transform clauses to textual CNF notation required by the BDD
        not_connective = BDDModel.NOT
        or_connective = " " + BDDModel.OR + " "
        and_connective = " " + BDDModel.AND + " "
        cnf_list = []
        for clause in self.clauses:
            cnf_list.append(
                "("
                + or_connective.join(
                    list(
                        map(
                            lambda elem: not_connective + self.features[abs(elem)]
                            if elem < 0
                            else self.features[abs(elem)],
                            clause,
                        )
                    )
                )
                + ")"
            )
        cnf_formula = and_connective.join(cnf_list)
        self.destination_model = BDDModel.from_cnf_formula(cnf_formula, 
                                                           list(self.variables.keys()))
        return self.destination_model
