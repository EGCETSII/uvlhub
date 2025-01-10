from typing import Any, Optional
from functools import total_ordering

from flamapy.core.exceptions import FlamaException
from flamapy.core.models import AST, VariabilityModel, VariabilityElement, ASTOperation
from flamapy.core.models.ast import simplify_formula, propagate_negation, to_cnf


class Relation:
    def __init__(
        self, parent: "Feature", children: list["Feature"], card_min: int, card_max: int
    ) -> None:
        self.parent = parent
        self.children = children
        self.card_min = card_min
        self.card_max = card_max

    def add_child(self, feature: "Feature") -> None:
        self.children.append(feature)

    def is_mandatory(self) -> bool:
        return self.card_min == 1 and self.card_max == 1 and len(self.children) == 1

    def is_optional(self) -> bool:
        return self.card_min == 0 and self.card_max == 1 and len(self.children) == 1

    def is_or(self) -> bool:
        return (
            self.card_min == 1
            and self.card_max == len(self.children)
            and len(self.children) > 1
        )

    def is_alternative(self) -> bool:
        return self.card_min == 1 and self.card_max == 1 and len(self.children) > 1

    def is_mutex(self) -> bool:
        return self.card_min == 0 and self.card_max == 1 and len(self.children) > 1

    def is_cardinal(self) -> bool:
        return (
            self.is_group()
            and not self.is_alternative()
            and not self.is_or()
            and not self.is_mutex()
        )

    def is_group(self) -> bool:
        return len(self.children) > 1

    def __str__(self) -> str:
        parent_name = self.parent.name if self.parent else ""
        res = f"{parent_name}[{self.card_min},{self.card_max}]"
        for _child in self.children:
            res += _child.name + " "
        if self.is_alternative():
            relation_type = "alternative"
        elif self.is_or():
            relation_type = "or"
        elif self.is_mandatory():
            relation_type = "mandatory"
        elif self.is_optional():
            relation_type = "optional"
        elif self.is_mutex():
            relation_type = "mutex"
        elif self.is_cardinal():
            relation_type = "cardinality"
        else:
            relation_type = "Other"
        res = f"({relation_type}) " + res
        return res

    def __hash__(self) -> int:
        return hash(
            (self.parent, frozenset(self.children), self.card_min, self.card_max)
        )

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, Relation)
            and self.parent == other.parent
            and sorted(self.children) == sorted(other.children)
            and self.card_min == other.card_min
            and self.card_max == other.card_max
        )

    def __lt__(self, other: Any) -> bool:
        return str(self) < str(other)


@total_ordering
class Feature(VariabilityElement):

    def __init__(
        self,
        name: str,
        relations: Optional[list["Relation"]] = None,
        parent: Optional["Feature"] = None,
        is_abstract: bool = False,
    ):
        super().__init__(name)
        self.name = name
        self.relations = [] if relations is None else relations
        self.parent = self._get_parent() if parent is None else parent
        self.is_abstract = is_abstract
        self.attributes = list["Attribute"]([])

    def is_empty(self) -> bool:
        return self.parent is None and self.relations == []

    def add_relation(self, relation: "Relation") -> None:
        self.relations.append(relation)
        for child in relation.children:
            child.parent = self

    def add_attribute(self, attribute: "Attribute") -> None:
        attribute.parent = self
        self.attributes.append(attribute)

    def get_attributes(self) -> list["Attribute"]:
        return self.attributes

    def set_attributes(self, attributes: list["Attribute"]) -> None:
        self.attributes = attributes

    def get_relations(self) -> list["Relation"]:
        return self.relations

    def get_parent(self) -> Optional["Feature"]:
        return self.parent

    def _get_parent(self) -> Optional["Feature"]:
        return next((r.parent for r in self.get_relations() if not r.children), None)

    def get_children(self) -> list["Feature"]:
        """Direct children of the feature regardless the relation type."""
        return [f for r in self.get_relations() for f in r.children]

    def is_root(self) -> bool:
        return self.parent is None

    def is_mandatory(self) -> bool:
        return self.parent is not None and any(
            r.is_mandatory() and self in r.children for r in self.parent.get_relations()
        )

    def is_optional(self) -> bool:
        return self.parent is not None and any(
            r.is_optional() and self in r.children for r in self.parent.get_relations()
        )

    def is_or_group(self) -> bool:
        return any(r.is_or() for r in self.get_relations())

    def is_alternative_group(self) -> bool:
        return any(r.is_alternative() for r in self.get_relations())

    def is_mutex_group(self) -> bool:
        return any(r.is_mutex() for r in self.get_relations())

    def is_cardinality_group(self) -> bool:
        return any(r.is_cardinal() for r in self.get_relations())

    def is_group(self) -> bool:
        return any(r.is_group() for r in self.get_relations())

    def is_multiple_group_decomposition(self) -> bool:
        return sum(r.is_group() for r in self.get_relations()) > 1

    def is_leaf(self) -> bool:
        return len(self.get_relations()) == 0

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Feature) and self.name == other.name

    def __lt__(self, other: Any) -> bool:
        return str(self) < str(other)


class Constraint:
    def __init__(self, name: str, ast: AST):
        self.name = name
        self._ast = ast

    @property
    def ast(self) -> AST:
        return self._ast

    @ast.setter
    def ast(self, ast: AST) -> None:
        self._ast = ast

    def get_features(self) -> list[str]:
        """List of features' names involved in the constraint."""
        features = set()
        stack = [self.ast.root]
        while stack:
            node = stack.pop()
            if node.is_unique_term():
                features.add(node.data)
            elif node.is_unary_op():
                stack.append(node.left)
            elif node.is_binary_op():
                stack.append(node.right)
                stack.append(node.left)
        return list(features)

    def is_simple_constraint(self) -> bool:
        """Return true if the constraint is a simple constraint (requires or excludes)."""
        return self.is_requires_constraint() or self.is_excludes_constraint()

    def is_complex_constraint(self) -> bool:
        """Return true if the constraint is a complex constraint
        (i.e., it is not a simple constraint)."""
        return not self.is_simple_constraint()

    def is_requires_constraint(self) -> bool:
        """Return true if the constraint is a requires constraint."""
        root_op = self._ast.root
        if root_op.is_binary_op():
            if root_op.data in [ASTOperation.REQUIRES, ASTOperation.IMPLIES]:
                return root_op.left.is_term() and root_op.right.is_term()

            if root_op.data == ASTOperation.OR:
                neg_left = (
                    root_op.left.data == ASTOperation.NOT
                    and root_op.left.left.is_term()
                )
                neg_right = (
                    root_op.right.data == ASTOperation.NOT
                    and root_op.right.left.is_term()
                )
                return (
                    neg_left
                    and root_op.right.is_term()
                    or neg_right
                    and root_op.left.is_term()
                )
        return False

    def is_excludes_constraint(self) -> bool:
        """Return true if the constraint is an excludes constraint."""
        root_op = self._ast.root
        if root_op.is_binary_op():
            if root_op.data in [ASTOperation.EXCLUDES, ASTOperation.XOR]:
                return root_op.left.is_term() and root_op.right.is_term()

            if root_op.data in [ASTOperation.REQUIRES, ASTOperation.IMPLIES]:
                neg_right = (
                    root_op.right.data == ASTOperation.NOT
                    and root_op.right.left.is_term()
                )
                return root_op.left.is_term() and neg_right

            if root_op.data == ASTOperation.OR:
                neg_left = (
                    root_op.left.data == ASTOperation.NOT
                    and root_op.left.left.is_term()
                )
                neg_right = (
                    root_op.right.data == ASTOperation.NOT
                    and root_op.right.left.is_term()
                )
                return neg_left and neg_right
        return False

    def is_pseudocomplex_constraint(self) -> bool:
        """Return true if the constraint is a pseudo-complex constraint
        (i.e., it can be transformed to a set of simple constraints)."""
        split_ctcs = split_constraint(self)
        return len(split_ctcs) > 1 and all(
            self.is_simple_constraint() for ctc in split_ctcs
        )

    def is_strictcomplex_constraint(self) -> bool:
        """Return true if the constraint is a strict-complex constraint
        (i.e., it cannot be transformed to a set of simple constraints)."""
        split_ctcs = split_constraint(self)
        return any(self.is_complex_constraint() for ctc in split_ctcs)

    def __str__(self) -> str:
        return f"({self.name}) {str(self.ast)}"

    def __hash__(self) -> int:
        return hash(str(self.ast).lower())

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, Constraint)
            and str(self.ast).lower() == str(other.ast).lower()
        )

    def __lt__(self, other: Any) -> bool:
        return str(self.ast).lower() < str(other.ast).lower()


class FeatureModel(VariabilityModel):
    @staticmethod
    def get_extension() -> str:
        return "fm"

    def __init__(
        self, root: "Feature", constraints: Optional[list["Constraint"]] = None
    ) -> None:
        self.root = root
        self.ctcs = [] if constraints is None else constraints

    def get_relations(self, feature: Optional["Feature"] = None) -> list["Relation"]:
        if self.root is None or self.root.is_empty():
            return []
        if feature is None:
            feature = self.root
        relations = []
        for relation in feature.relations:
            relations.append(relation)
            for _feature in relation.children:
                relations.extend(self.get_relations(_feature))
        return relations

    def get_features(self) -> list["Feature"]:
        features: list["Feature"] = []
        if self.root is not None:
            features.append(self.root)
            for relation in self.get_relations():
                features.extend(relation.children)
        return features

    def get_constraints(self) -> list["Constraint"]:
        return self.ctcs

    def get_mandatory_features(self) -> list["Feature"]:
        return [f for f in self.get_features() if f.is_mandatory()]

    def get_optional_features(self) -> list["Feature"]:
        return [f for f in self.get_features() if f.is_optional()]

    def get_alternative_group_features(self) -> list["Feature"]:
        return [f for f in self.get_features() if f.is_alternative_group()]

    def get_or_group_features(self) -> list["Feature"]:
        return [f for f in self.get_features() if f.is_or_group()]

    def get_feature_by_name(self, feature_name: str) -> Optional["Feature"]:
        return next((f for f in self.get_features() if f.name == feature_name), None)

    def get_complex_constraints(self) -> list["Constraint"]:
        return [c for c in self.get_constraints() if c.is_complex_constraint()]

    def get_simple_constraints(self) -> list["Constraint"]:
        return [c for c in self.get_constraints() if c.is_simple_constraint()]

    def get_pseudocomplex_constraints(self) -> list["Constraint"]:
        return [c for c in self.get_constraints() if c.is_pseudocomplex_constraint()]

    def get_strictcomplex_constraints(self) -> list["Constraint"]:
        return [c for c in self.get_constraints() if c.is_strictcomplex_constraint()]

    def get_excludes_constraints(self) -> list["Constraint"]:
        return [c for c in self.get_constraints() if c.is_excludes_constraint()]

    def get_requires_constraints(self) -> list["Constraint"]:
        return [c for c in self.get_constraints() if c.is_requires_constraint()]

    def import_model(
        self, root: Feature, parent: Feature, ctcs: list[Constraint]
    ) -> None:
        root.parent = parent
        for ctc in ctcs:
            if ctc not in self.ctcs:
                self.ctcs.append(ctc)

    def __str__(self) -> str:
        res = "root: " + ("None" if self.root is None else self.root.name) + "\r\n"
        res += "Relations:\r\n"
        for i, relation in enumerate(self.get_relations()):
            res += f"R{i}: {relation}\r\n"
        for i, ctc in enumerate(self.ctcs):
            res += f"CTC{i}: {ctc}\r\n"
        attributes_res = ""
        for feature in self.get_features():
            for attribute in feature.get_attributes():
                attributes_res += f"{attribute}" + "\r\n"
        if attributes_res != "":
            res += "Attributes:\r\n" + attributes_res
        return res

    def __hash__(self) -> int:
        return hash(
            (
                self.root,
                frozenset(self.get_features()),
                frozenset(self.get_relations()),
                frozenset(self.ctcs),
            )
        )

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, FeatureModel)
            and self.root == other.root
            and sorted(self.get_features()) == sorted(other.get_features())
            and sorted(self.get_relations()) == sorted(other.get_relations())
            and sorted(self.get_constraints()) == sorted(other.get_constraints())
        )


class Range:
    def __init__(self, min_value: int, max_value: int):
        self.min_value: int = min_value
        self.max_value: int = max_value

    def __str__(self) -> str:
        return "[ " + str(self.min_value) + " to " + str(self.max_value) + "]"


class Domain:
    def __init__(
        self, ranges: Optional[list["Range"]], elements: Optional[list["Any"]]
    ):
        self.range_list = [] if ranges is None else ranges
        self.element_list = [] if elements is None else elements

    def get_range_list(self) -> list["Range"]:
        return self.range_list

    def get_element_list(self) -> list["Any"]:
        return self.element_list

    def add_range(self, new_range: Range) -> None:
        self.range_list.append(new_range)

    def add_element(self, element: Any) -> None:
        self.element_list.append(element)

    def set_range_list(self, range_list: list["Range"]) -> None:
        self.range_list = range_list

    def set_element_list(self, element_list: list["Any"]) -> None:
        self.element_list = element_list

    def __str__(self) -> str:
        result = ""
        element_list = self.element_list
        if len(element_list) > 0:
            result = str(element_list)

        range_list = self.range_list
        if len(range_list) > 0:
            result = result + "Integer"
            for rng in range_list:
                result = result + str(rng)

        return result


class Attribute:
    def __init__(
        self,
        name: str,
        domain: Optional[Domain] = None,
        default_value: Any = None,
        null_value: Optional["Any"] = None,
    ):
        self.name: "str" = name
        self.parent: Optional["Feature"] = None
        self.domain: Optional["Domain"] = domain
        self.default_value: "Any" = default_value
        self.null_value: Optional[Any] = null_value

    def get_name(self) -> str:
        return self.name

    def get_parent(self) -> Optional["Feature"]:
        return self.parent

    def get_domain(self) -> Domain:
        if self.domain is None:
            raise FlamaException("Attribute domain is not defined")
        return self.domain

    def get_default_value(self) -> Any:
        return self.default_value

    def get_null_value(self) -> Any:
        return self.null_value

    def set_name(self, name: str) -> None:
        self.name = name

    def set_parent(self, parent: Feature) -> None:
        self.parent = parent

    def set_domain(self, domain: Domain) -> None:
        self.domain = domain

    def set_default_value(self, default_value: Any) -> None:
        self.default_value = default_value

    def set_null_value(self, null_value: Any) -> None:
        self.null_value = null_value

    def __str__(self) -> str:
        if self.parent is None:
            raise TypeError("self.parent is None, expected Feature type")

        result = "[" + self.parent.name + "." + self.name + "]"
        if self.domain is not None:
            result = result + "Domain: " + str(self.domain)
        if self.default_value is not None:
            result = result + "Default value: " + str(self.default_value)
        if self.null_value is not None:
            result = result + "Null value: " + str(self.null_value)

        return result


# This is a list of ultils to work with constraints
def get_new_ctc_name(ctcs_names: list[str], prefix_name: str) -> str:
    """Return a new name for a constraint (based on the provided prefix) that is not already
    in the given list of constraints' names."""
    count = 1
    new_name = f"{prefix_name}"
    while new_name in ctcs_names:
        new_name = f"{prefix_name}{count}"
        count += 1
    return new_name


def left_right_features_from_simple_constraint(
    simple_ctc: Constraint,
) -> tuple[str, str]:
    """Return the names of the features involved in a simple constraint.

    A simple constraint can be a requires constraint or an excludes constraint.
    A requires constraint can be represented in the AST of the constraint with one of the
    following structures:
        A requires B
        A => B
        !A v B
    An excludes constraint can be represented in the AST of the constraint with one of the
    following structures:
        A excludes B
        A => !B
        !A v !B
    """
    root_op = simple_ctc.ast.root
    if root_op.data in [
        ASTOperation.REQUIRES,
        ASTOperation.IMPLIES,
        ASTOperation.EXCLUDES,
    ]:
        left = root_op.left.data
        right = root_op.right.data
        if right == ASTOperation.NOT:
            right = root_op.right.left.data
    elif root_op.data == ASTOperation.OR:
        left = root_op.left.data
        right = root_op.right.data
        if left == ASTOperation.NOT and right == ASTOperation.NOT:  # excludes
            left = root_op.left.left.data
            right = root_op.right.left.data
        elif left == ASTOperation.NOT:  # implies: A -> B
            left = root_op.left.left.data
            right = root_op.right.data
        elif right == ASTOperation.NOT:  # implies: B -> A
            left = root_op.right.left.data
            right = root_op.left.data
    return (left, right)


def split_constraint(constraint: Constraint) -> list[Constraint]:
    """Given a constraint, split it in multiple constraints separated by the AND operator."""
    asts = split_formula(constraint.ast)
    asts_simplified = [simplify_formula(ast) for ast in asts]
    asts = []
    for ctc in asts_simplified:
        asts.extend(split_formula(ctc))

    asts_negation_propagated = [propagate_negation(ast.root) for ast in asts]
    asts = []
    for ctc in asts_negation_propagated:
        asts.extend(split_formula(ctc))

    asts_cnf = [to_cnf(ast) for ast in asts]
    asts = []
    for ctc in asts_cnf:
        asts.extend(split_formula(ctc))
    return [Constraint(f"{constraint.name}{i}", ast) for i, ast in enumerate(asts)]


def split_formula(formula: AST) -> list[AST]:
    """Given a formula, returns a list of formulas separated by the AND operator."""
    res = []
    node = formula.root
    if node.data == ASTOperation.AND:
        res.extend(split_formula(AST(node.left)))
        res.extend(split_formula(AST(node.right)))
    else:
        res.append(formula)
    return res
