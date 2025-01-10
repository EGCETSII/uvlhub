from typing import Any, Optional, cast
from collections import defaultdict

from flamapy.core.models import VariabilityModel
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.bdd_metamodel.models import BDDModel
from flamapy.metamodels.bdd_metamodel.operations.interfaces import FeatureInclusionProbability
from flamapy.metamodels.bdd_metamodel.operations import BDDConfigurationsNumber


class BDDFeatureInclusionProbability(FeatureInclusionProbability):
    """The Feature Inclusion Probability (FIP) operation determines the probability
    for a variable to be included in a valid solution.

    Ref.: [Heradio et al. 2019. Supporting the Statistical Analysis of Variability Models.
    (https://doi.org/10.1109/ICSE.2019.00091)]
    """

    def __init__(self) -> None:
        self._result: dict[Any, float] = {}
        self._partial_configuration: Optional[Configuration] = None

    def set_partial_configuration(self, partial_configuration: Optional[Configuration]) -> None:
        self._partial_configuration = partial_configuration

    def execute(self, model: VariabilityModel) -> 'BDDFeatureInclusionProbability':
        bdd_model = cast(BDDModel, model)
        self._result = feature_inclusion_probability(bdd_model, self._partial_configuration)
        #self.result = variable_probabilities_single_traverse(bdd_model)
        return self

    def get_result(self) -> dict[Any, float]:
        return self._result

    def feature_inclusion_probability(self) -> dict[Any, float]:
        return self.get_result()


def feature_inclusion_probability(bdd_model: BDDModel,
                                  config: Optional[Configuration] = None) -> dict[Any, float]:
    n_configs_op = BDDConfigurationsNumber()
    n_configs_op.set_partial_configuration(config)
    total_configs = n_configs_op.execute(bdd_model).get_result()
    if total_configs == 0:
        return {feature: 0.0 for feature in bdd_model.variables}

    prob: dict[Any, float] = defaultdict(float)
    if config is None:
        for feature in bdd_model.variables:
            values = {feature: True}
            u_func = bdd_model.bdd.let(values, bdd_model.root)
            n_vars = len(bdd_model.variables) - len(values)
            prob[feature] = bdd_model.bdd.count(u_func, nvars=n_vars) / total_configs
    else:
        values = dict(config.elements.items())
        for feature in bdd_model.variables:
            feature_selected = values.get(feature, None)    
            values = {feature: True}
            u_func = bdd_model.bdd.let(values, bdd_model.root)
            n_vars = len(bdd_model.variables) - len(values)
            prob[feature] = bdd_model.bdd.count(u_func, nvars=n_vars) / total_configs
            if feature_selected is None:
                values.pop(feature)
            else:
                values[feature] = feature_selected
    return prob


## TODO: The following is the optimized implementation from UNED 
## Algoritm available in the paper: https://doi.org/10.1109/ICSE.2019.00091
## Currently, the implementation is not correct at all.

# def feature_inclusion_probability(bdd_model: BDDModel,
#                                   config: Optional[Configuration] = None) -> dict[Any, float]:
#     print(bdd_model.bdd.var_levels)
#     root = bdd_model.root
#     id_root = bdd_model.get_value(root, bdd_model.negated(root))
#     prob: dict[int, float] = defaultdict(float)
#     prob[id_root] = 1/2
#     mark: dict[int, bool] = defaultdict(bool)
#     get_node_pr(bdd_model, root, prob, mark, bdd_model.negated(root))
#     print(bdd_model.bdd.var_levels)
#     print(f'PROBS: {len(prob)}')
#     for v, p in prob.items():
#         print(f'Value (id): {v} ({type(v)}) -> {p}')
#     joint_prob: dict[int, float] = defaultdict(float)
#     joint_prob_nodes_n: dict[tuple[int, Any], float] = defaultdict(float)
#     joint_prob_nodes_phi: dict[tuple[int, Any], float] = defaultdict(float)
#     cond_prob: dict[tuple[int, Any], float] = defaultdict(float)
#     mark: dict[int, bool] = defaultdict(bool)
#     get_joint_pr(bdd_model, root, prob, joint_prob, joint_prob_nodes_n, joint_prob_nodes_phi, cond_prob, mark, bdd_model.negated(root))
#     print(f'COND PROBS: {len(cond_prob)}')
#     for v, p in cond_prob.items():
#         print(f'Value (id): {v} -> {p}')
#     print(f'JOINT PROBS NODES: {len(joint_prob)}')
#     # for v, p in joint_prob_nodes.items():
#     #     print(f'Value (id): {v} -> {p}')
#     print(f'JOINT PROBS: {len(joint_prob)}')
#     for v, p in joint_prob.items():
#         print(f'Index: {v} -> {p}')
#     #total_prob = prob[bdd_model.get_value(bdd_model.get_terminal_node_n1())]
#     #total_prob = prob[bdd_model.get_value(bdd_model.get_terminal_node_n1())]
#     #total_prob = prob[bdd_model.get_value(bdd_model.get_terminal_node_n1(), bdd_model.negated(root))]
#     total_prob = prob[bdd_model.get_value(bdd_model.get_terminal_node_n1(), bdd_model.negated(root))]
#     print(f'Total Prob: {total_prob}')
#     fip: dict[Any, float] = {}
#     print(bdd_model.bdd.var_levels)
#     for xj in bdd_model.variables:
#         xj_node = bdd_model.get_node(xj)
#         xj_id = bdd_model.index(xj_node)
#         fip[xj] = joint_prob[xj_id] / total_prob
#         print(f'{bdd_model.pretty_node_str(xj_node)} -> {fip[xj]}')
#     return fip


# def get_node_pr(bdd_model: BDDModel,
#                 node: Any,  # _bdd.Function | int
#                 prob: dict[int, float], 
#                 mark: dict[int, bool], 
#                 complemented: bool) -> None:
#     id_node = bdd_model.get_value(node, complemented)
#     mark[id_node] = not mark[id_node]

#     if not bdd_model.is_terminal_node(node):

#         # explore low
#         low = bdd_model.get_low_node(node)
#         id_low = bdd_model.get_value(low, complemented)
#         if bdd_model.is_terminal_node(low):
#             prob[id_low] = prob[id_low] + prob[id_node]
#         else:
#             prob[id_low] = prob[id_low] + (prob[id_node] / 2)
#         if mark[id_node] != mark[id_low]:
#             get_node_pr(bdd_model, low, prob, mark, complemented ^ bdd_model.negated(low))

#         # explore high
#         high = bdd_model.get_high_node(node)
#         id_high = bdd_model.get_value(high, complemented)
#         if bdd_model.is_terminal_node(high):
#             prob[id_high] = prob[id_high] + prob[id_node]
#         else:
#             prob[id_high] = prob[id_high] + (prob[id_node] / 2)
#         if mark[id_node] != mark[id_high]:
#             get_node_pr(bdd_model, high, prob, mark, complemented ^ bdd_model.negated(high))


# def get_joint_pr(bdd_model: BDDModel,
#                  node: Any,  # _bdd.Function | int
#                  prob: dict[int, float], 
#                  joint_prob: dict[int, float],
#                  joint_prob_nodes_n: dict[tuple[int, Any], float],
#                  joint_prob_nodes_phi: dict[tuple[int, Any], float],
#                  cond_prob: dict[tuple[int, Any], float],
#                  mark: dict[int, bool], 
#                  complemented: bool) -> None:
#     id_node = bdd_model.get_value(node, complemented)
#     mark[id_node] = not mark[id_node]

#     if not bdd_model.is_terminal_node(node):

#         # explore low
#         low = bdd_model.get_low_node(node)
#         id_low = bdd_model.get_value(low, complemented)
#         if bdd_model.is_terminal_n0(low):
#             cond_prob[(id_node, False)] = 0.0
#         elif bdd_model.is_terminal_n1(low):
#             cond_prob[(id_node, False)] = 1.0
#         else:
#             if mark[id_node] != mark[id_low]:
#                 get_joint_pr(bdd_model, low, prob, joint_prob, joint_prob_nodes_n, joint_prob_nodes_phi, cond_prob, mark, complemented ^ bdd_model.negated(low))
#             cond_prob[(id_node, False)] = joint_prob_nodes_phi[(id_low, None)] / (2 * prob[id_low])
#         joint_prob_nodes_n[(id_node, False)] = cond_prob[(id_node, False)] * prob[id_node]
        
#         # explore high
#         high = bdd_model.get_high_node(node)
#         id_high = bdd_model.get_value(high, complemented)
#         if bdd_model.is_terminal_n0(high):
#             cond_prob[(id_node, True)] = 0.0
#         elif bdd_model.is_terminal_n1(high):
#             cond_prob[(id_node, True)] = 1.0
#         else:
#             if mark[id_node] != mark[id_high]:
#                 get_joint_pr(bdd_model, high, prob, joint_prob, joint_prob_nodes_n, joint_prob_nodes_phi, cond_prob, mark, complemented ^ bdd_model.negated(high))
#             cond_prob[(id_node, True)] = joint_prob_nodes_phi[(id_high, None)] / (2 * prob[id_high])
#         joint_prob_nodes_n[(id_node, True)] = cond_prob[(id_node, True)] * prob[id_node]

#         # Combine both low and high
#         joint_prob_nodes_phi[(id_node, None)] = joint_prob_nodes_phi[(id_node, True)] + joint_prob_nodes_phi[(id_node, False)]
#         joint_prob[bdd_model.index(node)] = prob[bdd_model.index(node)] + joint_prob_nodes_n[(id_node, True)]

#         # Add joint probabilities of the removed nodes
#         for xj in range(bdd_model.index(node) + 1, bdd_model.index(high)):
#             joint_prob[xj] = joint_prob[xj] + (joint_prob_nodes_n[(id_node, True)] / 2)
#         for xj in range(bdd_model.index(node) + 1, bdd_model.index(low)):
#             joint_prob[xj] = joint_prob[xj] + (joint_prob_nodes_n[(id_node, False)] / 2)
