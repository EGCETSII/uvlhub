from typing import Optional
from enum import Enum, auto

from flamapy.core.exceptions import FlamaException


class CNFLogicConnective(Enum):
    """The propositional logic connectives a formula in CNF can contain."""

    NOT = auto()
    AND = auto()
    OR = auto()


class TextCNFNotation(Enum):
    """Possible notations of a CNF formula.

    Five different notations are available:
        Logical symbols:
            (A) ∧ (¬B ∨ C) ∧ ...
        Textual symbols:
            (A) and (not B or C) and ...
        Java symbols:
            (A) && (!B || C) && ...
        Java Short symbols:
            (A) & (!B | C) && ...
        Short symbols:
            (A) & (-B | C) & ...
    """

    LOGICAL = {
        CNFLogicConnective.NOT: "¬",
        CNFLogicConnective.AND: "∧",
        CNFLogicConnective.OR: "∨",
    }
    TEXTUAL = {
        CNFLogicConnective.NOT: "not",
        CNFLogicConnective.AND: "and",
        CNFLogicConnective.OR: "or",
    }
    JAVA = {
        CNFLogicConnective.NOT: "!",
        CNFLogicConnective.AND: "&&",
        CNFLogicConnective.OR: "||",
    }
    JAVA_SHORT = {
        CNFLogicConnective.NOT: "!",
        CNFLogicConnective.AND: "&",
        CNFLogicConnective.OR: "|",
    }
    SHORT = {
        CNFLogicConnective.NOT: "-",
        CNFLogicConnective.AND: "&",
        CNFLogicConnective.OR: "|",
    }


class TextCNFModel:
    """Textual representation of a conjunctive normal form (CNF) formula.

    A CNF formula (or clausal normal form) is a conjunction of one or more clauses,
    where a clause is a disjunction of literals.
    """

    def __init__(self) -> None:
        self._cnf_formula: Optional[str] = None
        self._cnf_notation: Optional[TextCNFNotation] = None
        self._variables: list[str] = []  # list of str with variables' names

    def from_textual_cnf(self, cnf_formula: str) -> None:
        self._cnf_formula = cnf_formula
        self._cnf_notation = identify_notation(cnf_formula)
        self._variables = extract_variables(cnf_formula)

    def from_textual_cnf_file(self, filepath: str) -> None:
        """This method reads any of the available textual notations,
        but only one notation at the same time,
        so the .txt file should include only one of the possible notations in a single line.
        """
        with open(filepath, "r", encoding="utf-8") as file:
            self.from_textual_cnf(file.readline())

    def write_textual_cnf_file(
        self, filepath: str, syntax: TextCNFNotation = TextCNFNotation.JAVA_SHORT
    ) -> None:
        """Write the textual CNF formula as a string in a file.

        Default syntax is TextCNFNotation.JAVA_SHORT: (A) & (!B | C) && ...
        """
        cnf_formula = self.get_textual_cnf_formula(syntax)
        with open(filepath, "w+", encoding="utf-8") as file:
            file.write(cnf_formula)

    def get_textual_cnf_notation(self) -> TextCNFNotation:
        """Return the notation used for the CNF formula."""
        if self._cnf_formula is None:
            raise FlamaException("CNF Model not initialized. Use a `from_` method first.")
        assert self._cnf_notation is not None
        return self._cnf_notation

    def get_textual_cnf_formula(
        self, syntax: TextCNFNotation = TextCNFNotation.JAVA_SHORT
    ) -> str:
        """Return the CNF formula in the specified notation syntax.

        Default syntax is TextCNFNotation.JAVA_SHORT: (A) & (!B | C) && ...
        """
        if self._cnf_formula is None:
            raise FlamaException("CNF Model not initialized. Use a `from_` method first.")
        assert self._cnf_notation is not None

        cnf_formula = self._cnf_formula
        cnf_notation = self._cnf_notation

        if syntax == cnf_notation:
            return cnf_formula

        # Translate AND operators
        symbol_pattern = " " + cnf_notation.value[CNFLogicConnective.AND] + " "
        new_symbol = " " + syntax.value[CNFLogicConnective.AND] + " "
        cnf_formula = cnf_formula.replace(symbol_pattern, new_symbol)

        # Translate OR operators
        symbol_pattern = " " + cnf_notation.value[CNFLogicConnective.OR] + " "
        new_symbol = " " + syntax.value[CNFLogicConnective.OR] + " "
        cnf_formula = cnf_formula.replace(symbol_pattern, new_symbol)

        # Translate NOT operators
        # This is more complex because the symbol may be part of a feature's name
        if cnf_notation == TextCNFNotation.TEXTUAL:
            symbol_pattern = cnf_notation.value[CNFLogicConnective.NOT] + " "
            new_symbol = syntax.value[CNFLogicConnective.NOT]
            cnf_formula = cnf_formula.replace(symbol_pattern, new_symbol)
        elif syntax == TextCNFNotation.TEXTUAL:
            symbol_pattern = " " + cnf_notation.value[CNFLogicConnective.NOT]
            new_symbol = " " + syntax.value[CNFLogicConnective.NOT] + " "
            cnf_formula = cnf_formula.replace(symbol_pattern, new_symbol)

            symbol_pattern = "(" + cnf_notation.value[CNFLogicConnective.NOT]
            new_symbol = "(" + syntax.value[CNFLogicConnective.NOT] + " "
            cnf_formula = cnf_formula.replace(symbol_pattern, new_symbol)
        else:
            symbol_pattern = " " + cnf_notation.value[CNFLogicConnective.NOT]
            new_symbol = " " + syntax.value[CNFLogicConnective.NOT]
            cnf_formula = cnf_formula.replace(symbol_pattern, new_symbol)

            symbol_pattern = "(" + cnf_notation.value[CNFLogicConnective.NOT]
            new_symbol = "(" + syntax.value[CNFLogicConnective.NOT]
            cnf_formula = cnf_formula.replace(symbol_pattern, new_symbol)
        return cnf_formula

    def get_variables(self) -> list[str]:
        """Return the list of variables' names in the CNF formula."""
        if self._cnf_formula is None:
            raise FlamaException("CNF Model not initialized. Use a `from_` method first.")
        return self._variables


def identify_notation(cnf_formula: str) -> TextCNFNotation:
    """Return the notation used by the given CNF formula.

    Default TextCNFNotation.JAVA.
    """
    notation = check_unary_connective(cnf_formula)
    if notation is None or notation in (
        TextCNFNotation.JAVA,
        TextCNFNotation.JAVA_SHORT,
    ):
        notation = check_binary_connective(cnf_formula)
    if notation is None:
        notation = TextCNFNotation.JAVA_SHORT
    return notation


def check_unary_connective(cnf_formula: str) -> Optional[TextCNFNotation]:
    symbol = TextCNFNotation.LOGICAL.value[CNFLogicConnective.NOT]
    if " " + symbol in cnf_formula or "(" + symbol in cnf_formula:
        return TextCNFNotation.LOGICAL

    symbol = TextCNFNotation.SHORT.value[CNFLogicConnective.NOT]
    if " " + symbol in cnf_formula or "(" + symbol in cnf_formula:
        return TextCNFNotation.SHORT

    symbol = TextCNFNotation.TEXTUAL.value[CNFLogicConnective.NOT]
    if " " + symbol + " " in cnf_formula or "(" + symbol + " " in cnf_formula:
        return TextCNFNotation.TEXTUAL

    symbol = TextCNFNotation.JAVA.value[CNFLogicConnective.NOT]  # JAVA or JAVA_SHORT
    if " " + symbol in cnf_formula or "(" + symbol in cnf_formula:
        return TextCNFNotation.JAVA

    return None


def check_binary_connective(cnf_formula: str) -> Optional[TextCNFNotation]:
    for notation in TextCNFNotation:
        for connective in notation.value.keys():
            if connective != CNFLogicConnective.NOT:
                symbol = notation.value[connective]
                symbol_pattern = " " + symbol + " "
                if symbol_pattern in cnf_formula:
                    return notation
    return None


def extract_variables(cnf_formula: str) -> list[str]:
    """Return the list of variables' names of the CNF formula."""
    variables = set()
    cnf_notation = identify_notation(cnf_formula)

    # Remove initial and final parenthesis
    and_symbol_pattern = " " + cnf_notation.value[CNFLogicConnective.AND] + " "
    clauses = list(
        map(lambda c: c[1:len(c) - 1], cnf_formula.split(and_symbol_pattern))
    )

    # Remove final parenthesis of last clause (because of the possible end of line: '\n')
    if ")" in clauses[len(clauses) - 1]:
        clauses[len(clauses) - 1] = clauses[len(clauses) - 1][:-1]

    for clause in clauses:
        tokens = clause.split(" ")
        tokens = list(
            filter(lambda t: t != cnf_notation.value[CNFLogicConnective.OR], tokens)
        )
        for feature in tokens:
            if feature == cnf_notation.value[CNFLogicConnective.NOT]:
                continue
            if feature.startswith(cnf_notation.value[CNFLogicConnective.NOT]):
                variables.add(
                    feature.replace(cnf_notation.value[CNFLogicConnective.NOT], "", 1)
                )
            else:
                variables.add(feature)
    return list(variables)
