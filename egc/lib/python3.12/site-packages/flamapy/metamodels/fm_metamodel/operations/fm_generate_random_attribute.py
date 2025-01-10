import random
from typing import Any, cast

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Operation
from flamapy.core.exceptions import FlamaException
from flamapy.metamodels.fm_metamodel.models import (
    FeatureModel, 
    Range,
    Domain, 
    Attribute
)


class GenerateRandomAttribute(Operation):
    """
    This operation generate random values for a given attribute and set the attribute for all
    features in the model.
    """

    def __init__(self) -> None:
        self.result: FeatureModel
        self._attribute_name: str = ''
        self._attribute_domain: Domain
        self._only_leaf_features: bool = False

    def get_result(self) -> FeatureModel:
        return self.result

    def set_name(self, attribute_name: str) -> None:
        self._attribute_name = attribute_name

    def set_domain(self, attribute_domain: Domain) -> None:
        self._attribute_domain = attribute_domain

    def set_only_leaf_features(self, only_leaf_features: bool) -> None:
        self._only_leaf_features = only_leaf_features

    def execute(self, model: VariabilityModel) -> 'GenerateRandomAttribute':
        if model is None:
            raise FlamaException("Invalid feature model.")
        if self._attribute_name is None:
            raise FlamaException("Attribute's name has not been provided.")
        if self._attribute_domain is None:
            raise FlamaException("Attribute's domain has not been provided.")
        fm_model = cast(FeatureModel, model)
        self.result = generate_random_attribute_values(fm_model, 
                                                       self._attribute_name, 
                                                       self._attribute_domain,
                                                       self._only_leaf_features)
        return self


def generate_random_attribute_values(feature_model: FeatureModel, 
                                     name: str,
                                     domain: Domain,
                                     only_leaf_features: bool) -> FeatureModel:
    for feature in feature_model.get_features():
        if not only_leaf_features or only_leaf_features and feature.is_leaf():
            if not any(name == attr.name for attr in feature.get_attributes()):
                random_value = get_random_value_from_domain(domain)
                new_attribute = Attribute(name, domain, random_value)
                feature.add_attribute(new_attribute)
    return feature_model


def get_random_value_from_domain(domain: Domain) -> Any:
    """Generate a random value from a domain.
    NOTE: This is not uniform if there are more than one range or a range and a list of elements.
    """
    elements_in_domain = domain.get_element_list()
    ranges = domain.get_range_list()
    if elements_in_domain and ranges:
        random_element = random.choice(elements_in_domain)
        random_range_value = get_random_value_from_ranges(ranges)
        random_value = random.choice([random_element, random_range_value])
    elif elements_in_domain:
        random_value = random.choice(elements_in_domain)
    elif ranges:
        random_value = get_random_value_from_ranges(ranges)
    else:
        random_value = None
    return random_value


def get_random_value_from_ranges(ranges: list[Range]) -> Any:
    """Generate a random value from a list of ranges.
    NOTE: This is not uniform if there are more than one range.
    """
    random_range = random.choice(ranges)
    if isinstance(random_range.min_value, float) or isinstance(random_range.max_value, float):
        min_digits = str(random_range.min_value)[::-1].find('.')
        max_digits = str(random_range.max_value)[::-1].find('.')
        digits = max(min_digits, max_digits)
        value = round(random.uniform(random_range.min_value, random_range.max_value), digits)
    elif isinstance(random_range.min_value, int) and isinstance(random_range.max_value, int):
        value = random.randint(random_range.min_value, random_range.max_value)
    else:
        raise FlamaException(f"Invalid range for attribute: {ranges}")
    return value
