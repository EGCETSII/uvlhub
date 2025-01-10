import sys
from typing import Optional
from xml.etree import ElementTree

from flamapy.core.transformations import TextToModel
from flamapy.core.models.ast import AST, ASTOperation
from flamapy.core.exceptions import DuplicatedFeature, FlamaException
from flamapy.metamodels.fm_metamodel.models import (
    Constraint,
    Feature,
    FeatureModel,
    Relation,
)


class XMLReader(TextToModel):

    @staticmethod
    def get_source_extension() -> str:
        return 'xml'

    def __init__(self, path: str) -> None:
        self.path = path
        # TODO: add empty FeatureModel
        # self.model = FeatureModel(feature, [])
        self.name_feature: dict[str, Feature] = {}

    def transform(self) -> FeatureModel:
        rootcounter = 1
        tree = ElementTree.parse(self.path)
        xml_root = tree.getroot()
        # iterate over child of the xml root element
        for child in xml_root:
            if child.tag.casefold() == 'feature':
                rootcounter += 1
                root = self.parse_feature(child, None)
                feature_model = FeatureModel(root, [])
            elif child.tag.casefold() == 'excludes' or child.tag.casefold() == 'requires':
                ctc = self.parse_ctc(child)
                feature_model.ctcs.append(ctc)
            else:
                print("This XML contains non supported elements", file=sys.stderr)

        return feature_model

    def parse_ctc(self, element: ElementTree.Element) -> Constraint:
        origin: Optional[Feature] = None
        destination: Optional[Feature] = None

        name = element.attrib.get('name')
        if name is None:
            raise FlamaException('name is not defined')

        ctc_type = element.tag.casefold()

        el_feature = element.attrib.get('feature')

        if el_feature in self.name_feature:
            origin = self.name_feature[el_feature]

        el_exclude = element.attrib.get('excludes')
        el_require = element.attrib.get('requires')
        if ctc_type == 'excludes' and el_exclude in self.name_feature:
            destination = self.name_feature[el_exclude]
            operator_type = ASTOperation.EXCLUDES
        elif ctc_type == 'requires' and el_require in self.name_feature:
            destination = self.name_feature[el_require]
            operator_type = ASTOperation.REQUIRES

        if origin is None or destination is None:
            raise FlamaException('origin or destination not found')

        return Constraint(
            name,
            AST.create_simple_binary_operation(operator_type, origin.name, destination.name)
        )

    def parse_feature(self, element: ElementTree.Element, parent: Optional[Feature]) -> Feature:
        name = str(element.attrib.get('name'))

        feature = Feature(name, [], parent=parent)

        if name in self.name_feature:
            print("This XML contains duplicated feature names", file=sys.stderr)
            raise DuplicatedFeature

        self.name_feature[name] = feature

        for child in element:
            if feature is not None and (
                child.tag.casefold() == "setrelation"
                or child.tag.casefold() == "binaryrelation"
            ):
                relation = self.parse_relation(child, feature)
                relation.parent = feature
                feature.relations.append(relation)
        return feature

    def parse_relation(self, element: ElementTree.Element, parent: Feature) -> Relation:
        relation = Relation(parent=parent, children=[], card_min=0, card_max=0)

        if element.tag.casefold() == 'binaryrelation':
            num_solitary_features = 0

            for child in element:
                if child.tag.casefold() == 'solitaryfeature':
                    num_solitary_features += 1
                    feature = self.parse_feature(child, parent)
                    relation.children.append(feature)
                elif child.tag.casefold() == 'cardinality':
                    relation.card_min = int(str(child.attrib.get('min')))
                    relation.card_max = int(str(child.attrib.get('max')))
                else:
                    print("This XML contains non supported elements", file=sys.stderr)

        elif element.tag.casefold() == 'setrelation':
            for child in element:
                if child.tag.casefold() == 'groupedfeature':
                    feature = self.parse_feature(child, parent)
                    relation.children.append(feature)
                elif child.tag.casefold() == 'cardinality':
                    relation.card_min = int(str(child.attrib.get('min')))
                    relation.card_max = int(str(child.attrib.get('max')))
                else:
                    print("This XML contains non supported elements", file=sys.stderr)
        else:
            raise RuntimeError("Something is wrong on the xml")
        return relation
