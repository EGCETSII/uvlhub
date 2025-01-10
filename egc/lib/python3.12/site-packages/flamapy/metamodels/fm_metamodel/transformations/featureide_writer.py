from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.dom import minidom
from typing import Any 

from flamapy.core.models.ast import Node, ASTOperation
from flamapy.core.transformations import ModelToText

from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Constraint, Relation
from flamapy.metamodels.fm_metamodel.transformations import FeatureIDEReader


class FeatureIDEWriter(ModelToText):

    CTC_TYPES = {ASTOperation.NOT: FeatureIDEReader.TAG_NOT,
                 ASTOperation.AND: FeatureIDEReader.TAG_CONJ,
                 ASTOperation.OR: FeatureIDEReader.TAG_DISJ,
                 ASTOperation.XOR: FeatureIDEReader.TAG_ALT,
                 ASTOperation.IMPLIES: FeatureIDEReader.TAG_IMP,
                 ASTOperation.REQUIRES: FeatureIDEReader.TAG_IMP,
                 ASTOperation.EXCLUDES: FeatureIDEReader.TAG_IMPN,
                 ASTOperation.EQUIVALENCE: FeatureIDEReader.TAG_EQ}

    @staticmethod
    def get_destination_extension() -> str:
        return '.xml'

    def __init__(self, path: str, source_model: FeatureModel) -> None:
        self._path = path
        self._source_model = source_model

    def transform(self) -> str:
        fm_tree = _to_featureidexml(self._source_model).getroot()
        xml_str = ElementTree.tostring(fm_tree, 
                                       encoding='UTF-8', 
                                       method='xml', 
                                       xml_declaration=True)
        xml_str = prettify(xml_str)
        if self._path is not None:
            with open(self._path, 'wb') as file:
                file.write(xml_str)
        return xml_str


def _to_featureidexml(feature_model: FeatureModel) -> ElementTree.ElementTree:
    fm_element = ElementTree.Element(FeatureIDEReader.TAG_FEATUREMODEL)
    tree = ElementTree.ElementTree(fm_element)
    struct = ElementTree.SubElement(fm_element, FeatureIDEReader.TAG_STRUCT)
    constraints = ElementTree.SubElement(fm_element, FeatureIDEReader.TAG_CONSTRAINTS)
    root = ElementTree.SubElement(struct, 
                                  _tag_element(feature_model.root), 
                                  _get_attributes(feature_model.root))
    _create_tree(root, feature_model.root.get_relations())
    _get_constraints(constraints, feature_model.get_constraints())
    return tree


def _create_tree(parent_element: Element, relations: list[Relation]) -> None:
    for rel in relations:
        for child in rel.children:
            new_elem = ElementTree.SubElement(parent_element,
                                              _tag_element(child),
                                              _get_attributes(child))
            _create_tree(new_elem, child.get_relations())


def _get_attributes(feature: Feature) -> dict[str, str]:
    atributes = {}
    if feature.is_mandatory(): 
        atributes['mandatory'] = 'true'
    if feature.is_abstract: 
        atributes['abstract'] = 'true'
    atributes['name'] = feature.name
    return atributes


def _tag_element(feature: Feature) -> str:
    if feature.is_leaf(): 
        name = FeatureIDEReader.TAG_FEATURE
    else: 
        if feature.is_or_group(): 
            name = FeatureIDEReader.TAG_OR
        elif feature.is_alternative_group(): 
            name = FeatureIDEReader.TAG_ALT
        else: 
            name = FeatureIDEReader.TAG_AND
    return name


def _get_constraints(parent_element: Element, constraints: list[Constraint]) -> None:
    for const in _get_constraints_info(constraints):
        rule = ElementTree.SubElement(parent_element, FeatureIDEReader.TAG_RULE)
        new_constraint = ElementTree.SubElement(rule, const['ast']['type'])
        for operand in const['ast']['operands']:
            _create_elem_constraint(operand, new_constraint)


def _create_elem_constraint(operand: dict[str, Any], parent_element: Element) -> None:
    elem = ElementTree.SubElement(parent_element, operand['type'])
    if operand['type'] == FeatureIDEReader.TAG_VAR:
        elem.text = operand['operands'][0]
    if len(operand['operands']) > 1 or operand['type'] == FeatureIDEReader.TAG_NOT:
        for operation in operand['operands']:
            _create_elem_constraint(operation, elem)


def _get_constraints_info(constraints: list[Constraint]) -> list[dict[str, Any]]:
    constraints_info = []
    for ctc in constraints:
        ctc_info: dict[str, Any] = {}
        ctc_info['name'] = ctc.name
        ctc_info['expr'] = ctc.ast.pretty_str()
        ctc_info['ast'] = _get_ctc_info(ctc.ast.root)
        constraints_info.append(ctc_info)
    return constraints_info


def _get_ctc_info(ast_node: Node) -> dict[str, Any]:
    ctc_info: dict[str, Any] = {}
    if ast_node.is_term():
        ctc_info['type'] = FeatureIDEReader.TAG_VAR
        ctc_info['operands'] = [ast_node.data]
    else:
        ctc_info['type'] = FeatureIDEWriter.CTC_TYPES[ast_node.data]
        operands = []
        left = _get_ctc_info(ast_node.left)
        operands.append(left)
        if ast_node.right is not None:
            right = _get_ctc_info(ast_node.right)
            operands.append(right)
        ctc_info['operands'] = operands
    return ctc_info


def prettify(xml: str) -> bytes:
    """Return a pretty-printed XML string for the Element."""
    reparsed = minidom.parseString(xml)
    return reparsed.toprettyxml(indent="\t", encoding='UTF-8')
