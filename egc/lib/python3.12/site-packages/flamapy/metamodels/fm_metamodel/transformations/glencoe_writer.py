import json
from typing import Any

from flamapy.core.models.ast import Node, ASTOperation
from flamapy.core.transformations import ModelToText
from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Constraint


class GlencoeWriter(ModelToText):
    CTC_TYPES = {
        ASTOperation.NOT: "NotTerm",
        ASTOperation.AND: "AndTerm",
        ASTOperation.OR: "OrTerm",
        ASTOperation.XOR: "XorTerm",
        ASTOperation.IMPLIES: "ImpliesTerm",
        ASTOperation.REQUIRES: "ImpliesTerm",
        ASTOperation.EXCLUDES: "ExcludesTerm",
        ASTOperation.EQUIVALENCE: "EquivalentTerm",
    }

    @staticmethod
    def get_destination_extension() -> str:
        return "gfm.json"

    def __init__(self, path: str, source_model: FeatureModel) -> None:
        self.path = path
        self.source_model = source_model

    def transform(self) -> str:
        json_object = _to_json(self.source_model)
        if self.path is not None:
            with open(self.path, "w", encoding="utf8") as file:
                json.dump(json_object, file, indent=4)
        return json.dumps(json_object, indent=4)


def _to_json(feature_model: FeatureModel) -> dict[str, Any]:
    result: dict[str, Any] = {}
    result["id"] = f"FM_{feature_model.root.name}"
    result["name"] = f"FM_{feature_model.root.name}"
    result["features"] = _get_features_info(feature_model.get_features())
    result["tree"] = _get_tree_info(feature_model.root)
    result["constraints"] = _get_constraints_info(feature_model.get_constraints())
    return result


def _get_features_info(features: list[Feature]) -> dict[str, Any]:
    features_info = {}
    for feature in sorted(features, key=lambda f: f.name):
        feature_type = "FEATURE"
        if feature.is_alternative_group():
            feature_type = "XOR"
        elif feature.is_or_group():
            feature_type = "OR"
        elif feature.is_cardinality_group():
            feature_type = "GENOR"

        features_info[feature.name] = {
            "name": feature.name,
            "optional": not feature.is_mandatory(),
            "type": feature_type,
            "note": "",  # ToDo: add 'note' attribute information
        }

        if feature_type == "GENOR":
            relation = next(r for r in feature.get_relations() if r.is_cardinal())
            features_info[feature.name]["min"] = relation.card_min
            features_info[feature.name]["max"] = relation.card_max
    return features_info


def _get_tree_info(feature: Feature) -> dict[str, Any]:
    feature_info: dict[str, Any] = {}
    feature_info["id"] = feature.name
    children = [
        _get_tree_info(child)
        for child in sorted(feature.get_children(), key=lambda f: f.name)
    ]
    if children:
        feature_info["children"] = children
    return feature_info


def _get_constraints_info(constraints: list[Constraint]) -> dict[str, Any]:
    constraints_info = {}
    for ctc in constraints:
        constraints_info[ctc.name] = _get_ctc_info(ctc.ast.root)
    return constraints_info


def _get_ctc_info(ast_node: Node) -> dict[str, Any]:
    ctc_info: dict[str, Any] = {}
    if ast_node.is_term():
        ctc_info["type"] = "FeatureTerm"
        ctc_info["operands"] = [ast_node.data]
    else:
        ctc_info["type"] = GlencoeWriter.CTC_TYPES[ast_node.data]
        operands = []
        left = _get_ctc_info(ast_node.left)
        operands.append(left)
        if ast_node.right is not None:
            right = _get_ctc_info(ast_node.right)
            operands.append(right)
        ctc_info["operands"] = operands
    return ctc_info
