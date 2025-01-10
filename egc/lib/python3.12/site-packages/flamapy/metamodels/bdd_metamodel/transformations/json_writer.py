import os
import tempfile

from flamapy.metamodels.bdd_metamodel.transformations._bdd_writer import BDDWriter


class JSONWriter(BDDWriter):

    @staticmethod
    def get_destination_extension() -> str:
        return 'json'

    def transform(self) -> str:
        if self.path is None:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf8') as file:
                self.path = file.name
                result = write_to_file(self)
                self.path = None
        else:
            result = write_to_file(self)
        return result


def write_to_file(writer: JSONWriter) -> str:
    super(type(writer), writer).transform()
    with open(writer.path, 'r', encoding='utf8') as file:
        result = os.linesep.join(file.readlines())
    return result
