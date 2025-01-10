from flamapy.core.exceptions import FlamaException
from flamapy.metamodels.bdd_metamodel.transformations._bdd_writer import BDDWriter


class PickleWriter(BDDWriter):

    @staticmethod
    def get_destination_extension() -> str:
        return 'p'

    def transform(self) -> str:
        if not self._roots:
            try:
                self.source_model.bdd.dump(filename=self.path)
            except Exception:
                roots = [self.source_model.root]
        else:
            roots = [self.source_model.root]
            try:
                self.source_model.bdd.dump(filename=self.path, roots=roots)
            except Exception as exc:
                raise FlamaException('PickleWriter is not supported.') from exc
        return ''