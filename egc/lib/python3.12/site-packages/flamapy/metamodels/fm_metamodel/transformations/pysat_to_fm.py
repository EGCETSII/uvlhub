import functools
from typing import Optional

from flamapy.core.models.ast import AST, Node, ASTOperation
from flamapy.core.transformations import ModelToModel
from flamapy.core.exceptions import FlamaException
from flamapy.metamodels.fm_metamodel.models.feature_model import (
    FeatureModel,
    Constraint,
    Feature,
    Relation,
)
from flamapy.metamodels.pysat_metamodel.models import PySATModel


class PysatToFM(ModelToModel):

    @staticmethod
    def get_source_extension() -> str:
        return 'pysat'

    @staticmethod
    def get_destination_extension() -> str:
        return 'fm'

    def __init__(self, source_model: PySATModel) -> None:
        self.source_model: PySATModel = source_model
        self.counter: int = 1
        self.destination_model: Optional[FeatureModel] = None

    def transform(self) -> FeatureModel:
        # Create the tree with the root and all children as optional features
        root_feature = self._identify_root()
        children_features = [Feature(v) 
                             for v in self.source_model.variables.keys()
                             if v != root_feature.name]
        for child in children_features:
            child.parent = root_feature
            optional_relation = Relation(root_feature, [child], 0, 1)
            root_feature.add_relation(optional_relation)

        # Create the constraints from the clauses
        count = 1
        constraints = []
        for clause in self.source_model.get_all_clauses():
            if len(clause) != 1:
                node = functools.reduce(lambda left, right: Node(ASTOperation.OR,
                                        self._get_node_from_clause_term(left),
                                        self._get_node_from_clause_term(right)),
                                        clause)
                constraints.append(Constraint(f'CTC{count}', AST(node)))
                count += 1

        feature_model = FeatureModel(root_feature, constraints)
        self.destination_model = feature_model
        return feature_model

    def _identify_root(self) -> Feature:
        for clause in self.source_model.get_all_clauses():
            if len(clause) == 1:
                return Feature(self.source_model.features[clause[0]])
        raise FlamaException('Error converting from SAT to FM. ',
                             'There is not candidate for the root feature.')

    def _get_node_from_clause_term(self, term: Node | int) -> Node:
        if isinstance(term, Node):
            return term
        name = self.source_model.features[abs(term)]
        return Node(name) if term >= 0 else Node(ASTOperation.NOT, Node(name))
