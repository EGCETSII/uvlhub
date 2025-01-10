import re

from flamapy.core.models.ast import ASTOperation
from flamapy.core.transformations import ModelToText
from flamapy.metamodels.fm_metamodel.models import (
    Constraint,
    Feature,
    FeatureModel,
    Relation,
)


class UVLWriter(ModelToText):
    @staticmethod
    def get_destination_extension() -> str:
        return "uvl"

    def __init__(self, path: str, source_model: FeatureModel):
        self.path = path
        self.model = source_model

    def transform(self) -> str:
        model = self.model
        root = model.root

        serialized_model = (
            self.read_features(root, "features", 0) + "\n" + self.read_constraints()
        )

        if self.path is not None:
            with open(self.path, "w", encoding="utf8") as file:
                file.write(serialized_model)
        return serialized_model

    def read_features(self, feature: Feature, result: str, tab_count: int) -> str:
        tab_count = tab_count + 1
        result = (
            result
            + "\n"
            + tab_count * "\t"
            + feature.name
            + " "
            + self.read_attributes(feature)
        )
        tab_count = tab_count + 1
        for relation in feature.relations:
            relation_name = self.serialize_relation(relation)
            result = result + "\n" + tab_count * "\t" + relation_name
            for feature_node in relation.children:
                result = self.read_features(feature_node, result, tab_count)
        return result

    @classmethod
    def read_attributes(cls, feature: Feature) -> str:
        attributes = []
        if feature.is_abstract:
            attributes.append("abstract")
        for attribute in feature.get_attributes():
            attribute_str = attribute.name
            if attribute.default_value is not None:
                if isinstance(attribute.default_value, str):
                    attribute_str += f" '{attribute.default_value}'"
                elif isinstance(attribute.default_value, bool):
                    attribute_str += f" {str(attribute.default_value).lower()}"
                else:
                    attribute_str += f" {attribute.default_value}"
            attributes.append(attribute_str)
        return f'{{{", ".join(attributes)}}}' if attributes else ""

    @staticmethod
    def serialize_relation(rel: Relation) -> str:
        result = ""

        if rel.is_alternative():
            result = "alternative"
        elif rel.is_mandatory():
            result = "mandatory"
        elif rel.is_optional():
            result = "optional"
        elif rel.is_or():
            result = "or"
        else:
            min_value = rel.card_min
            max_value = rel.card_max
            if min_value == max_value:
                result = "[" + str(min_value) + "]"
            else:
                result = "[" + str(min_value) + ".." + str(max_value) + "]"

        return result

    def read_constraints(self) -> str:
        result = ""
        constraints = self.model.ctcs
        if constraints:
            result = "constraints"
            for constraint in constraints:
                constraint_text = self.serialize_constraint(constraint)
                result = result + "\n\t" + constraint_text
        return result

    @staticmethod
    def serialize_constraint(ctc: Constraint) -> str:
        return str(
            re.sub(
                rf"\b{ASTOperation.EXCLUDES.value}\b",
                "=> !",
                re.sub(
                    rf"\b{ASTOperation.REQUIRES.value}\b",
                    "=>",
                    re.sub(
                        rf"\b{ASTOperation.EQUIVALENCE.value}\b",
                        "<=>",
                        re.sub(
                            rf"\b{ASTOperation.IMPLIES.value}\b",
                            "=>",
                            re.sub(
                                rf"\b{ASTOperation.OR.value}\b",
                                "|",
                                re.sub(
                                    rf"\b{ASTOperation.AND.value}\b",
                                    "&",
                                    re.sub(
                                        rf"\b{ASTOperation.NOT.value}\b",
                                        "!",
                                        ctc.ast.pretty_str(),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            )
        )
