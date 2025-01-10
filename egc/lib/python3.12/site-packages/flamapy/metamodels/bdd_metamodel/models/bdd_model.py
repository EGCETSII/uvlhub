from enum import Enum
from typing import Optional, Any

# Low-level interface to pure Python implementation (wrapped by dd.autoref.BDD).
import dd.bdd as _dd_bdd
# Import the best available interface:
try:
    import dd.cudd as _bdd  # High-level interface to a C implementation.
except ImportError:
    import dd.autoref as _bdd  # High-level interface to pure Python implementation.


from flamapy.core.models import VariabilityModel


class BDDModel(VariabilityModel):
    """A Binary Decision Diagram (BDD) representation of the feature model.

    It relies on the dd library: https://pypi.org/project/dd/
    """

    class LogicConnective(Enum):
        NOT = '!'
        OR = '|'
        AND = '&'
        IMPLIES = '=>'
        EQUIVALENCE = '<=>'
        XOR = '^'

    @staticmethod
    def get_extension() -> str:
        return 'bdd'

    def __init__(self) -> None:
        self._bdd: _bdd.BDD = _bdd.BDD()  # BDD manager
        self._root: Optional[_bdd.Function | int] = None
        self._variables: list[Any] = []
        self._levels_variables: dict[int, Any] = {}

    @property
    def bdd(self) -> _bdd.BDD | _dd_bdd.BDD:
        return self._bdd

    @bdd.setter
    def bdd(self, new_bdd: _bdd.BDD | _dd_bdd.BDD) -> None:
        self._bdd = new_bdd
        self._variables = list(self._bdd.vars)
        self._root = next(iter(self._bdd.roots), None)
        self._levels_variables = {l: v for v, l in self._bdd.var_levels.items()}

    @property
    def root(self) -> _bdd.Function | int:
        return self._root

    @root.setter
    def root(self, new_root: _bdd.Function | int) -> None:
        self._root = new_root
        self._variables = list(self._bdd.vars)
        self._levels_variables = {l: v for v, l in self._bdd.var_levels.items()}

    @property
    def variables(self) -> list[Any]:
        return self._variables

    @classmethod
    def from_logic_formula(cls, formula: str, variables: list[Any]) -> 'BDDModel':
        """Build the BDD from a logic formula, and the list of variables.

        The logic formula can be a CNF formula or a propositional logic formula.
        """
        bdd_model = cls()
        # Store variables
        bdd_model._variables = variables
        # Declare variables
        bdd_model._bdd.declare(*variables)
        # Build the BDD
        bdd_model._root = bdd_model._bdd.add_expr(formula)

        # Reorder for optimization
        # Warning! Reordering may make the root starting to level > 0, and thus,
        # operations won't work correctly.
        # bdd_model._bdd.reorder()  

        # Levels and variables (dict for optimization)
        bdd_model._levels_variables = {l: v for v, l in bdd_model._bdd.var_levels.items()}
        return bdd_model

    def level_of_var(self, var: Any) -> Optional[int]:
        """Return the level of a given variable."""
        return self._bdd.var_levels.get(var, None)

    def var_at_level(self, level: int) -> Optional[Any]:
        """Return the variable at the given level."""
        return self._levels_variables.get(level, None)

    def var(self, node: _bdd.Function | int) -> Optional[Any]:
        """Return the variable of the node.

        It returns None if the node is a terminal node.
        """
        if self.is_terminal_node(node):
            return None
        if isinstance(node, int):
            level, _, _ = self._bdd.succ(node)
            return self.var_at_level(level)
        return node.var

    def level(self, node: _bdd.Function | int) -> Optional[int]:
        """Return the level of the node.

        Non-terminal nodes start at 0.
        Terminal nodes have level `s' being the `s' the number of variables.
        """
        #level, _, _ = self._bdd.succ(node)
        return self.level_of_var(self.var(node))

    def nof_nodes(self) -> int:
        """Return number of nodes in the BDD."""
        return len(self._bdd)

    def get_node(self, var: Any) -> _bdd.Function | int:
        """Return the node of the variable."""
        return self._bdd.var(var)

    def index(self, node: _bdd.Function | int) -> Optional[int]:
        """Position (index) of the variable that labels the node `n` in the ordering.

        Indexes start at 1.
        Terminal nodes (n0 and n1) have indexes `s + 1`, being `s' the number of variables.
        Note that index(n) = level(n) + 1.

        Example: node `n4` is labeled `B`, and `B` is in the 2nd position in ordering `[A,B,C]`,
        thus level(n4) = 2.
        """
        if self.is_terminal_node(node):
            return len(self.variables) + 1
        level = self.level(node)
        return level + 1 if level is not None else None

    def negated(self, node: _bdd.Function | int) -> bool:
        """Return whether the node is negated."""
        if isinstance(node, int):
            return node < 0
        return node.negated

    def get_terminal_node_n0(self) -> _bdd.Function | int:
        return self._bdd.false

    def get_terminal_node_n1(self) -> _bdd.Function | int:
        return self._bdd.true

    def is_terminal_node(self, node: _bdd.Function | int) -> bool:
        """Check if the node is a terminal node."""
        return self.is_terminal_n0(node) or self.is_terminal_n1(node)

    def is_terminal_n1(self, node: _bdd.Function | int) -> bool:
        """Check if the node is the terminal node 1 (n1)."""
        return node == self.get_terminal_node_n1()

    def is_terminal_n0(self, node: _bdd.Function | int) -> bool:
        """Check if the node is the terminal node 0 (n0)."""
        return node == self.get_terminal_node_n0()

    def get_high_node(self, node: _bdd.Function | int) -> Optional[_bdd.Function | int]:
        """Return the high (right, solid) node."""
        _, _, high = self._bdd.succ(node)
        return high

    def get_low_node(self, node: _bdd.Function | int) -> Optional[_bdd.Function | int]:
        """Return the low (left, dashed) node."""
        _, low, _ = self._bdd.succ(node)
        return low

    def get_value(self, node: _bdd.Function | int, complemented: bool = False) -> int:
        """Return the value (id) of the node considering complemented arcs."""
        value = int(node)
        if self.is_terminal_n0(node):
            value = 1 if complemented else 0
        elif self.is_terminal_n1(node):
            value = 0 if complemented else 1
        return value

    def pretty_node_str(self, node: _bdd.Function | int) -> str:
        return f'{self.var(node)} ' \
               f'(id: {self.get_value(node)}) ' \
               f'(level: {self.level(node)}) ' \
               f'(index: {self.index(node)}) '

    def __str__(self) -> str:
        result = 'Binary Decision Diagram (BDD):\n'
        result += f'Instance class: {type(self._bdd)}\n'
        result += f'#Nodes: {self.nof_nodes()}\n'
        result += f'Root: {self.pretty_node_str(self.root)}\n'
        levels_vars = dict(sorted(self._levels_variables.items(), key=lambda item: item[0]))
        for level, var in levels_vars.items():
            node = self.get_node(var)
            result += f' |-{self.pretty_node_str(node)}\n'
        result += f'Terminal node (n0): {self.pretty_node_str(self.get_terminal_node_n0())}\n'
        result += f'Terminal node (n1): {self.pretty_node_str(self.get_terminal_node_n1())}\n'
        return result
