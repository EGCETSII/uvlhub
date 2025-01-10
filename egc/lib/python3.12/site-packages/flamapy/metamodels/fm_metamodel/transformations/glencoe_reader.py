import functools
import json
from typing import Any, Optional

from flamapy.core.exceptions import FlamaException
from flamapy.core.models.ast import AST, Node, ASTOperation
from flamapy.core.transformations import TextToModel

from flamapy.metamodels.fm_metamodel.models import (
    FeatureModel,
    Feature,
    Relation,
    Constraint,
)


class GlencoeReader(TextToModel):
    @staticmethod
    def get_source_extension() -> str:
        return "gfm.json"

    def __init__(self, path: str) -> None:
        self.path = path

    def transform(self) -> FeatureModel:
        with open(self.path, "r", encoding="utf-8") as file:
            data = json.load(file)
            features_info = data["features"]
            root_node = data["tree"]
            constraints_info = data["constraints"]
            root_feature = self._parse_tree(None, root_node, features_info)
            constraints = self._parse_constraints(constraints_info, features_info)
            return FeatureModel(root_feature, constraints)

    def _parse_tree(
        self,
        parent: Optional[Feature],
        feature_node: dict[str, Any],
        features_info: dict[str, Any],
    ) -> Feature:
        """Parse the tree structure and returns the root feature."""
        feature_id = feature_node["id"]
        feature_type = features_info[feature_id]["type"]
        # optional = features_info[feature_id]['optional']
        feature = Feature(name=features_info[feature_id]["name"], parent=parent)

        if "children" in feature_node:
            children = []
            for child in feature_node["children"]:
                child_feature = self._parse_tree(feature, child, features_info)
                optional = features_info[child["id"]]["optional"]
                if feature_type == "FEATURE":  # simple feature (not group)
                    card_min = 0 if optional else 1
                    relation = Relation(feature, [child_feature], card_min, 1)
                    feature.add_relation(relation)
                elif not optional:
                    # Additional relation because Glencoe supports mandatory features in groups
                    relation = Relation(feature, [child_feature], 1, 1)
                    feature.add_relation(relation)
                    # children.append(child_feature)  # NOTE: may be needed for mandatory in groups
                else:
                    children.append(child_feature)
            if feature_type != "FEATURE":  # group
                if feature_type == "XOR":
                    relation = Relation(feature, children, 1, 1)
                elif feature_type == "OR":
                    relation = Relation(feature, children, 1, len(children))
                elif feature_type == "GENOR":  # Group Cardinality
                    card_min = features_info[feature_id]["min"]
                    card_max = features_info[feature_id]["max"]
                    relation = Relation(feature, children, card_min, card_max)
                feature.add_relation(relation)
        # Create an attribute for the 'note' parameter
        # note = features_info[feature_id]['note']
        # if note:
        #     pass
        return feature

    def _parse_constraints(
        self, ctcs_info: dict[str, Any], features_info: dict[str, Any]
    ) -> list[Constraint]:
        constraints = []
        for ctc_name, ctc_info in ctcs_info.items():
            ctc_node = self._parse_ast_constraint(ctc_info, features_info)
            constraints.append(Constraint(ctc_name, AST(ctc_node)))
        return constraints

    def _parse_ast_constraint(
        self, ctc_info: dict[str, Any], features_info: dict[str, Any]
    ) -> Node:
        ctc_type = ctc_info["type"]
        ctc_operands = ctc_info["operands"]
        node = None
        if ctc_type == "FeatureTerm":
            feature_id = ctc_info["operands"][0]
            feature_name = features_info[feature_id]["name"]
            node = Node(feature_name)
        elif ctc_type == "NotTerm":
            left = self._parse_ast_constraint(ctc_operands[0], features_info)
            node = Node(ASTOperation.NOT, left)
        elif ctc_type == "ImpliesTerm":
            left = self._parse_ast_constraint(ctc_operands[0], features_info)
            right = self._parse_ast_constraint(ctc_operands[1], features_info)
            node = Node(ASTOperation.IMPLIES, left, right)
        elif ctc_type == "ExcludesTerm":
            left = self._parse_ast_constraint(ctc_operands[0], features_info)
            right = self._parse_ast_constraint(ctc_operands[1], features_info)
            node = Node(ASTOperation.EXCLUDES, left, right)
        elif ctc_type == "EquivalentTerm":
            left = self._parse_ast_constraint(ctc_operands[0], features_info)
            right = self._parse_ast_constraint(ctc_operands[1], features_info)
            node = Node(ASTOperation.EQUIVALENCE, left, right)
        elif ctc_type == "AndTerm":
            op_list = [
                self._parse_ast_constraint(op, features_info) for op in ctc_operands
            ]
            node = functools.reduce(
                lambda lamb, r: Node(ASTOperation.AND, lamb, r), op_list
            )
        elif ctc_type == "OrTerm":
            op_list = [
                self._parse_ast_constraint(op, features_info) for op in ctc_operands
            ]
            node = functools.reduce(
                lambda lamb, r: Node(ASTOperation.OR, lamb, r), op_list
            )
        elif ctc_type == "XorTerm":
            op_list = [
                self._parse_ast_constraint(op, features_info) for op in ctc_operands
            ]
            node = functools.reduce(
                lambda lamb, r: Node(ASTOperation.XOR, lamb, r), op_list
            )
        else:
            raise FlamaException(f"Invalid constraint: {ctc_info}")
        return node
