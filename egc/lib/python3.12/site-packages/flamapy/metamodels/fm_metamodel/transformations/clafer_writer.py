import re
from enum import Enum
from typing import Any

from flamapy.core.transformations import ModelToText
from flamapy.core.models.ast import ASTOperation
from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Constraint


ATTRIBUTED_FEATURE = 'AttributedFeature'
INSTANCE = 'CP'


class ClaferAttributeType(Enum):
    BOOL = 'boolean'
    STRING = 'string'
    INT = 'integer'
    FLOAT = 'double'  # Be careful: In clafer theres is also a 'real' primitive type.


class ClaferWriter(ModelToText):
    """Transform a feature model to a Clafer format."""

    @staticmethod
    def get_destination_extension() -> str:
        return 'txt'

    def __init__(self, path: str, source_model: FeatureModel) -> None:
        self.path = path
        self.source_model = source_model

    def transform(self) -> str:
        clafer_str = fm_to_clafer(self.source_model)
        if self.path is not None:
            with open(self.path, 'w', encoding='utf8') as file:
                file.write(clafer_str)
        return clafer_str


def fm_to_clafer(feature_model: FeatureModel) -> str:
    result = read_features(feature_model.root, 0)
    # The root feature is always abstract in Clafer:
    result = f'abstract {result}'
    # Definition of attributes at the top of the model:
    result = attributes_definition(feature_model) + '\n' + result
    for ctc in feature_model.get_constraints():
        result += read_constraints(ctc)
    # Create an instance
    result += f'\n\n{INSTANCE} : {feature_model.root.name}\n'
    return result


def read_features(feature: Feature, tab_count: int) -> str:
    tabs = '\t' * tab_count  # Indentation
    result = tabs

    # Group type
    group_type = parse_group_type(feature)
    if group_type is not None:
        result += f'{group_type} '

    # Feature
    result += feature.name
    if feature.get_attributes():
        result += f' : {ATTRIBUTED_FEATURE}'
    if feature.is_optional():
        result += ' ?'

    # Feature's attributes
    tab_count += 1
    result += read_feature_attributes(feature, tab_count)

    # Children
    result += '\n'
    for child in feature.get_children():
        result += read_features(child, tab_count)
    return result


def read_feature_attributes(feature: Feature, tab_count: int) -> str:
    result = ''
    for attribute in feature.get_attributes():
        tabs = '\t' * tab_count
        attribute_value = ''
        if attribute.default_value is not None:
            if isinstance(attribute.default_value, str):
                attribute_value = f'"{attribute.default_value}"'
            elif isinstance(attribute.default_value, bool):
                attribute_value = f"{str(attribute.default_value).lower()}"
            else:
                attribute_value = f"{attribute.default_value}"
        result += f'\n{tabs}[{attribute.get_name()} = {attribute_value}]'
    return result


def parse_group_type(feature: Feature) -> str | None:
    group_type = None
    if feature.is_alternative_group():
        group_type = 'xor'
    elif feature.is_or_group():
        group_type = 'or'
    elif feature.is_cardinality_group():
        rel = next((r for r in feature.get_relations() if r.is_cardinal()), None)
        if rel is not None:
            group_type = str(rel.card_min) + ".." + str(rel.card_max)
    elif feature.is_mutex_group():
        group_type = 'mux'
    return group_type


def read_constraints(const: Constraint) -> str:
    result = ""
    constraint_text = serialize_constraint(const)
    result = "\n" + constraint_text
    return result


def serialize_constraint(ctc: Constraint) -> str:
    ctc_str = ctc.ast.pretty_str()
    ctc_str = re.sub(fr'\b{ASTOperation.NOT.value}\b', 'not', ctc_str)
    ctc_str = re.sub(fr'\b{ASTOperation.AND.value}\b', '&&', ctc_str)
    ctc_str = re.sub(fr'\b{ASTOperation.OR.value}\b', '||', ctc_str)
    ctc_str = re.sub(fr'\b{ASTOperation.IMPLIES.value}\b', '=>', ctc_str)
    ctc_str = re.sub(fr'\b{ASTOperation.EQUIVALENCE.value}\b', '<=>', ctc_str)
    ctc_str = re.sub(fr'\b{ASTOperation.REQUIRES.value}\b', '=>', ctc_str)
    ctc_str = re.sub(fr'\b{ASTOperation.EXCLUDES.value}\b', '=> not', ctc_str)
    return f'[{ctc_str}]'


def attributes_definition(feature_model: FeatureModel) -> str:
    attributes = {attribute.get_name(): parse_type_value(attribute.get_default_value()) 
                  for feature in feature_model.get_features() 
                  for attribute in feature.get_attributes()}
    result = ''
    if attributes:
        result = f'abstract {ATTRIBUTED_FEATURE}\n'
        for name, type in attributes.items():
            result += f'\t{name} -> {type}\n'
    return result


def parse_type_value(value: Any) -> str:
    if isinstance(value, bool):
        return ClaferAttributeType.BOOL.value
    if isinstance(value, int):
        return ClaferAttributeType.INT.value
    if isinstance(value, float):
        return ClaferAttributeType.FLOAT.value
    if isinstance(value, str):
        return ClaferAttributeType.STRING.value
    return ''
