from flamapy.core.operations import Commonality
from flamapy.core.models import VariabilityModel
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from .pysat_configurations import PySATConfigurations


class PySATCommonality(Commonality):

    def __init__(self) -> None:
        self.result: float = 0
        self.configuration = Configuration({})

    def set_configuration(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def get_commonality(self) -> float:
        return self.get_result()

    def get_result(self) -> float:
        return self.result

    def execute(self, model: VariabilityModel) -> 'PySATCommonality':
        pysat_products_op = PySATConfigurations()
        pysat_products_op.execute(model)
        products = pysat_products_op.get_result()

        feature = list(self.configuration.elements.keys())[0]

        count = 0
        for product in products:
            count = count + 1 if feature in product else count

        self.result = count / len(products)

        return self
