import json

try:
    import dd.cudd as _bdd
except ImportError:
    import dd.autoref as _bdd

from flamapy.core.transformations import TextToModel
from flamapy.metamodels.bdd_metamodel.models import BDDModel


class JSONReader(TextToModel):

    @staticmethod
    def get_source_extension() -> str:
        return 'json'

    def __init__(self, path: str) -> None:
        self.path: str = path
        self.preserve_original_ordering: bool = False

    def set_preserve_original_ordering(self, preserve_original_ordering: bool) -> None:
        self.preserve_original_ordering = preserve_original_ordering

    def transform(self) -> BDDModel:
        bdd_model = BDDModel()
        bdd_model.root = bdd_model.bdd.load(self.path)[0]
        if self.preserve_original_ordering:
            with open(self.path, 'r', encoding='utf8') as json_file:
                data = json.load(json_file)
                level_of_var = data['level_of_var'] 
                bdd_model.bdd.reorder(level_of_var)
        else:
            _bdd.reorder(bdd_model.bdd)
        return bdd_model
