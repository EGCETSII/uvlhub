import re
import itertools
from typing import Optional

from flamapy.core.models.ast import ASTOperation
from flamapy.core.transformations import ModelToModel
from flamapy.metamodels.fm_metamodel.models import FeatureModel, Relation, Constraint
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
        self.destination_model: Optional[BDDModel] = None

    def transform(self) -> BDDModel:
        formula, variables = traverse_feature_tree(self.source_model)
        self.destination_model = BDDModel.from_logic_formula(formula, variables)
        return self.destination_model


def traverse_feature_tree(feature_model: FeatureModel) -> tuple[str, list[str]]:
    """Traverse the feature tree from the root and return the propositional formula and 
    the list of variables (features's names).
    """
    if feature_model is None or feature_model.root is None:
        return ('', [])
    formula = [feature_model.root.name]  # The root is always present
    variables = []
    for feature in feature_model.get_features():
        variables.append(feature.name)
        for relation in feature.get_relations():
            formula.append(get_relation_formula(relation))
    for constraint in feature_model.get_constraints():
        formula.append(get_constraint_formula(constraint))
    propositional_formula = ' & '.join(f'({f})' for f in formula)
    return (propositional_formula, variables)


def get_relation_formula(relation: Relation) -> str:
    result = ''
    if relation.is_mandatory():
        result = get_mandatory_formula(relation)
    elif relation.is_optional():
        result = get_optional_formula(relation)
    elif relation.is_or():
        result = get_or_formula(relation)
    elif relation.is_alternative():
        result = get_alternative_formula(relation)
    elif relation.is_mutex():
        result = get_mutex_formula(relation)
    elif relation.is_cardinal():
        result = get_cardinality_formula(relation)
    return result


def get_mandatory_formula(relation: Relation) -> str:
    return f'{relation.parent.name} <=> {relation.children[0].name}'


def get_optional_formula(relation: Relation) -> str:
    return f'{relation.children[0].name} => {relation.parent.name}'


def get_or_formula(relation: Relation) -> str:
    return f'{relation.parent.name} <=> ({" | ".join(child.name for child in relation.children)})'


def get_alternative_formula(relation: Relation) -> str:
    formula = []
    for child in relation.children:
        children_negatives = set(relation.children) - {child}
        formula.append(f'{child.name} <=> '
                       f'({" & ".join("!" + f.name for f in children_negatives)} '
                       f'& {relation.parent.name})')
    return " & ".join(f'({f})' for f in formula)


def get_mutex_formula(relation: Relation) -> str:
    formula = []
    for child in relation.children:
        children_negatives = set(relation.children) - {child}
        formula.append(f'{child.name} <=> '
                       f'({" & ".join("!" + f.name for f in children_negatives)} '
                       f'& {relation.parent.name})')
    formula_str = " & ".join(f'({f})' for f in formula)
    return f'({relation.parent.name} <=> ' \
           f'!({" | ".join(child.name for child in relation.children)})) | ({formula_str})'


def get_cardinality_formula(relation: Relation) -> str:
    children = {child.name for child in relation.children}
    or_ctc = []
    for k in range(relation.card_min, relation.card_max + 1):
        combi_k = list(itertools.combinations(children, k))
        for positives in combi_k:
            negatives = children - set(positives)
            positives_and_ctc = f'{" & ".join(positives)}'
            negatives_and_ctc = f'{" & ".join("!" + f for f in negatives)}'
            if positives_and_ctc and negatives_and_ctc:
                and_ctc = f'{positives_and_ctc} & {negatives_and_ctc}'
            else:
                and_ctc = f'{positives_and_ctc}{negatives_and_ctc}'
            or_ctc.append(and_ctc) 
    formula_or_ctc = f'{" | ".join(or_ctc)}'
    return f'{relation.parent.name} <=> {formula_or_ctc}'


def get_constraint_formula(ctc: Constraint) -> str:
    return str(
        re.sub(rf"\b{ASTOperation.EXCLUDES.value}\b",
               f'{BDDModel.LogicConnective.IMPLIES.value} {BDDModel.LogicConnective.NOT.value}',
               re.sub(rf"\b{ASTOperation.REQUIRES.value}\b",
                      BDDModel.LogicConnective.IMPLIES.value,
                      re.sub(rf"\b{ASTOperation.EQUIVALENCE.value}\b", 
                             BDDModel.LogicConnective.EQUIVALENCE.value,
                             re.sub(rf"\b{ASTOperation.IMPLIES.value}\b",
                                    BDDModel.LogicConnective.IMPLIES.value,
                                    re.sub(rf"\b{ASTOperation.OR.value}\b",
                                           BDDModel.LogicConnective.OR.value,
                                           re.sub(rf"\b{ASTOperation.AND.value}\b",
                                                  BDDModel.LogicConnective.AND.value,
                                                  re.sub(rf"\b{ASTOperation.NOT.value}\b",
                                                         BDDModel.LogicConnective.NOT.value,
                                                         re.sub(rf"\b{ASTOperation.XOR.value}\b",
                                                                BDDModel.LogicConnective.XOR.value,
                                                                ctc.ast.pretty_str())))))))))
