import functools
import json
from typing import Any 

from flamapy.core.models.ast import Node, AST, ASTOperation
from flamapy.core.exceptions import ParsingException
from flamapy.core.transformations import TextToModel

from flamapy.metamodels.fm_metamodel.models import (
    FeatureModel, 
    Relation, 
    Feature, 
    Constraint, 
    Attribute
)

from flamapy.metamodels.fm_metamodel.transformations.json_writer import JSONFeatureType


class JSONReader(TextToModel):

    @staticmethod
    def get_source_extension() -> str:
        return '.json'

    def __init__(self, path: str) -> None:
        self.path = path

    def transform(self) -> str:
        with open(self.path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            features_info = data['features']
            constraints_info = data['constraints']
            root_feature = parse_tree(None, features_info)
            constraints = parse_constraints(constraints_info)
            return FeatureModel(root_feature, constraints)

    @staticmethod
    def parse_json(json_content: str) -> FeatureModel:
        features_info = json_content['features']
        constraints_info = json_content['constraints']
        root_feature = parse_tree(None, features_info)
        constraints = parse_constraints(constraints_info)
        return FeatureModel(root_feature, constraints)


def parse_tree(parent: Feature, feature_node: dict[str, Any]) -> Feature:
    """Parse the tree structure and returns the root feature."""
    feature_name = feature_node['name']
    is_abstract = feature_node['abstract']
    feature = Feature(name=feature_name, parent=parent, is_abstract=is_abstract)

    parse_attributes(feature, feature_node)
    parse_relations(feature, feature_node)  # recursive
    return feature


def parse_attributes(feature: Feature, feature_node: dict[str, Any]) -> None:
    if 'attributes' in feature_node:
        for attribute in feature_node['attributes']:
            attribute_name = attribute['name']
            if 'value' in attribute:
                attribute_value = attribute['value']
            else:
                attribute_value = None
            attr = Attribute(attribute_name, None, attribute_value, None)
            attr.set_parent(feature)
            feature.add_attribute(attr)


def parse_relations(feature: Feature, feature_node: dict[str, Any]) -> None:
    if 'relations' in feature_node:
        for relation in feature_node['relations']:
            children = []
            for child in relation['children']:
                child_feature = parse_tree(feature, child)
                children.append(child_feature)
            relation_type = relation['type']
            if relation_type == JSONFeatureType.OPTIONAL.value:
                new_relation = Relation(feature, children, 0, 1)
            elif relation_type == JSONFeatureType.MANDATORY.value:
                new_relation = Relation(feature, children, 1, 1)
            elif relation_type == JSONFeatureType.XOR.value:
                new_relation = Relation(feature, children, 1, 1)
            elif relation_type == JSONFeatureType.OR.value:
                new_relation = Relation(feature, children, 1, len(children))
            elif relation_type == JSONFeatureType.MUTEX.value:
                new_relation = Relation(feature, children, 0, 1)
            elif relation_type == JSONFeatureType.CARDINALITY.value:  # Group Cardinality
                card_min = relation['card_min']
                card_max = relation['card_max']
                new_relation = Relation(feature, children, card_min, card_max)
            feature.add_relation(new_relation)


def parse_constraints(constraints_info: dict[str, Any]) -> list[Constraint]:
    constraints = []
    for ctc_info in constraints_info:
        name = ctc_info['name']
        # ctc_expr = ctc_info['expr']  # not used
        ast_tree = ctc_info['ast']
        ctc_node = parse_ast_constraint(ast_tree)
        ctc = Constraint(name, AST(ctc_node))
        constraints.append(ctc)
    return constraints


def parse_ast_constraint(ctc_info: dict[str, Any]) -> Node:
    ctc_type = ctc_info['type']
    ctc_operands = ctc_info['operands']
    node = None
    if ctc_type == JSONFeatureType.FEATURE.value:
        feature_name = ctc_info['operands'][0]
        node = Node(feature_name)
    elif ctc_type == ASTOperation.NOT.value:
        left = parse_ast_constraint(ctc_operands[0])
        node = Node(ASTOperation.NOT, left)
    elif ctc_type == ASTOperation.IMPLIES.value:
        left = parse_ast_constraint(ctc_operands[0])
        right = parse_ast_constraint(ctc_operands[1])
        node = Node(ASTOperation.IMPLIES, left, right)
    elif ctc_type == ASTOperation.REQUIRES.value:
        left = parse_ast_constraint(ctc_operands[0])
        right = parse_ast_constraint(ctc_operands[1])
        node = Node(ASTOperation.REQUIRES, left, right)
    elif ctc_type == ASTOperation.EXCLUDES.value:
        left = parse_ast_constraint(ctc_operands[0])
        right = parse_ast_constraint(ctc_operands[1])
        node = Node(ASTOperation.EXCLUDES, left, right)
    elif ctc_type == ASTOperation.EQUIVALENCE.value:
        left = parse_ast_constraint(ctc_operands[0])
        right = parse_ast_constraint(ctc_operands[1])
        node = Node(ASTOperation.EQUIVALENCE, left, right)
    elif ctc_type == ASTOperation.AND.value:
        op_list = [parse_ast_constraint(op) for op in ctc_operands]
        node = functools.reduce(lambda l, r: Node(ASTOperation.AND, l, r), op_list)
    elif ctc_type == ASTOperation.OR.value:
        op_list = [parse_ast_constraint(op) for op in ctc_operands]
        node = functools.reduce(lambda l, r: Node(ASTOperation.OR, l, r), op_list)
    elif ctc_type == ASTOperation.XOR.value:
        op_list = [parse_ast_constraint(op) for op in ctc_operands]
        node = functools.reduce(lambda l, r: Node(ASTOperation.XOR, l, r), op_list)
    else:
        raise ParsingException(f'Invalid constraint in JSON: {ctc_info}')
    return node