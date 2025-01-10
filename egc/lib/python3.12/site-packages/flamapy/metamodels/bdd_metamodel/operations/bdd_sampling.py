import random
from typing import Optional, cast

from flamapy.core.models import VariabilityModel
from flamapy.core.exceptions import FlamaException
from flamapy.core.operations import Sampling
from flamapy.metamodels.configuration_metamodel.models import Configuration
from flamapy.metamodels.bdd_metamodel.models import BDDModel


class BDDSampling(Sampling):
    """Uniform Random Sampling (URS) using a Binary Decision Diagram (BDD).

    This is an adaptation of
    [Heradio et al. 2021.
    Uniform and Scalable Sampling of Highly Configurable Systems.
    Empirical Software Engineering]
    which relies on counting-based sampling inspired in the original Knuth algorithm.

    This implementation supports samples with and without replacement,
    as well as samples from a given partial configuration.
    """

    def __init__(self) -> None:
        self._result: list[Configuration] = []
        self._sample_size: int = 0
        self._with_replacement: bool = False
        self._partial_configuration: Optional[Configuration] = None

    def set_sample_size(self, sample_size: int) -> None:
        if sample_size < 0:
            raise FlamaException(f'Sample size {sample_size} cannot be negative.')
        self._sample_size = sample_size

    def set_with_replacement(self, with_replacement: bool) -> None:
        self._with_replacement = with_replacement

    def set_partial_configuration(self, partial_configuration: Configuration) -> None:
        self._partial_configuration = partial_configuration

    def get_result(self) -> list[Configuration]:
        return self._result

    def get_sample(self) -> list[Configuration]:
        return self.get_result()

    def execute(self, model: VariabilityModel) -> 'BDDSampling':
        bdd_model = cast(BDDModel, model)
        self._result = sample(bdd_model, 
                              self._sample_size, 
                              self._with_replacement, 
                              self._partial_configuration)
        return self


def sample(model: BDDModel, 
           sample_size: int, 
           with_replacement: bool,
           partial_configuration: Optional[Configuration]
           ) -> list[Configuration]:
    configurations = []
    for _ in range(sample_size):
        config = random_configuration(model, partial_configuration)
        configurations.append(config)

    if not with_replacement:
        set_configurations = set(configurations)
        while len(set_configurations) < sample_size:
            config = random_configuration(model, partial_configuration)
            set_configurations.add(config)

    return list(set_configurations)


def random_configuration(bdd_model: BDDModel,
                         p_config: Optional[Configuration] = None) -> Configuration:
    # Initialize the configurations and values for BDD nodes with already known features
    values = {} if p_config is None else dict(p_config.elements.items())

    # Set the BDD nodes with the already known features values
    u_func = bdd_model.bdd.let(values, bdd_model.root)

    care_vars = set(bdd_model.variables) - values.keys()
    n_vars = len(care_vars)
    for feature in care_vars:
        # Number of configurations with the feature selected
        v_sel = bdd_model.bdd.let({feature: True}, u_func)
        nof_configs_var_selected = bdd_model.bdd.count(v_sel, nvars=n_vars - 1)
        # Number of configurations with the feature unselected
        v_unsel = bdd_model.bdd.let({feature: False}, u_func)
        nof_configs_var_unselected = bdd_model.bdd.count(v_unsel, nvars=n_vars - 1)

        # Randomly select or not the feature
        selected = random.choices([True, False],
                                  [nof_configs_var_selected, nof_configs_var_unselected],
                                  k=1)[0]

        # Update configuration and BDD node for the new feature
        values[feature] = selected
        u_func = bdd_model.bdd.let({feature: selected}, u_func)

        n_vars -= 1
    return Configuration(values)
