from typing import Optional

from flamapy.core.transformations import ModelToText
from flamapy.metamodels.bdd_metamodel.models import BDDModel


class BDDWriter(ModelToText):

    def __init__(self, path: str, source_model: BDDModel) -> None:
        self._path: Optional[str] = path
        self._source_model: BDDModel = source_model
        self._roots: bool = True

    @property
    def path(self) -> Optional[str]:
        return self._path

    @path.setter
    def path(self, new_path: Optional[str]) -> None:
        self._path = new_path

    @property
    def source_model(self) -> BDDModel:
        return self._source_model

    def set_roots(self, roots: bool) -> None:
        self._roots = roots

    def transform(self) -> str:
        if not self._roots:
            try:
                self.source_model.bdd.dump(filename=self.path, 
                                           filetype=self.get_destination_extension())
            except Exception:
                roots = [self.source_model.root]
        else:
            roots = [self.source_model.root]
            self.source_model.bdd.dump(filename=self.path,
                                       roots=roots,
                                       filetype=self.get_destination_extension())
        return ''
