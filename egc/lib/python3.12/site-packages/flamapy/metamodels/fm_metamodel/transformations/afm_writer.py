from flamapy.core.transformations import ModelToText

from flamapy.core.models.ast import Node
from flamapy.metamodels.fm_metamodel.models import (
    Feature,
    FeatureModel,
    Relation,
    Attribute
)


class AFMWriter(ModelToText):

    @staticmethod
    def get_destination_extension() -> str:
        return 'afm'

    def __init__(self, path: str, source_model: FeatureModel):
        self.path = path
        self.model = source_model

    def transform(self) -> str:
        serialized_model = ""
        serialized_model += self.serialize_relationships()
        serialized_model += self.serialize_attributes()
        serialized_model += self.serialize_constraints()

        if self.path is not None:
            with open(self.path, 'w', encoding='utf8') as file:
                file.write(serialized_model)

        return serialized_model

    def serialize_relationships(self) -> str:
        result = "%Relationships\n"

        root_feature = self.model.root
        relationships = self.recursive_relationship_read(root_feature)

        return result + relationships + "\n"

    def recursive_relationship_read(self, feature: Feature) -> str:
        result = feature.name + " : "

        relations = feature.get_relations()

        children = []
        for relation in relations:
            result += " " + self.read_relation(relation)
            children += relation.children
        result += ";\n"
        for child in children:
            if len(child.get_relations()) > 0:
                result += self.recursive_relationship_read(child)

        return result

    @classmethod
    def read_relation(cls, relation: Relation) -> str:
        children = relation.children
        result = ""

        if len(children) == 1:
            child = children[0]
            if relation.card_min == 1 and relation.card_max == 1:
                result = child.name
            if relation.card_min == 0 and relation.card_max == 1:
                result = "[" + child.name + "]"
        else:
            result = "[" + str(relation.card_min) + "," + \
                str(relation.card_max) + "]"
            features = []
            for child in children:
                features.append(child.name)

            result += "{" + ' '.join(features) + "}"

        return result

    def serialize_attributes(self) -> str:
        result = "%Attributes\n"

        features = self.model.get_features()

        for feature in features:
            name = feature.name
            for attribute in feature.get_attributes():
                result += name + "." + self.read_attribute(attribute) + ";\n"

        return result + "\n"

    @classmethod
    def read_attribute(cls, attribute: Attribute) -> str:
        result = attribute.name + ": "

        domain = attribute.get_domain()

        if len(domain.get_range_list()) > 0:
            result += "Integer "
            for _range in domain.get_range_list():
                result += "[" + str(_range.min_value) + \
                    " to " + str(_range.max_value) + "]"

        if len(domain.get_element_list()) > 0:
            result += "[" + ",".join(domain.get_element_list()) + "]"

        result += "," + attribute.get_default_value()
        result += "," + attribute.get_null_value()

        return result

    def serialize_constraints(self) -> str:
        result = "%Constraints\n"

        constraints = self.model.get_constraints()

        for constraint in constraints:
            ast = constraint.ast
            root = ast.root
            result += self.recursive_constraint_read(root).strip() + ";\n"

        return result

    def recursive_constraint_read(self, node: Node) -> str:

        data = node.data
        if node.is_op():
            data = data.value.upper()

        if node.left and node.right:
            result = self.recursive_constraint_read(
                node.left) + data + self.recursive_constraint_read(node.right)
        elif not node.left and node.right:
            result = data + self.recursive_constraint_read(node.right)
        elif node.left and not node.right:
            result = self.recursive_constraint_read(node.left) + node.data
        else:
            result = " " + data + " "

        return result
