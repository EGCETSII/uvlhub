import os
import tempfile

from flamapy.core.exceptions import FlamaException
from flamapy.metamodels.bdd_metamodel.transformations._bdd_writer import BDDWriter


class DDDMPWriter(BDDWriter):

    @staticmethod
    def get_destination_extension() -> str:
        return 'dddmp'

    def transform(self) -> str:
        if self.path is None:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf8') as file:
                self.path = file.name
                result = write_to_file(self)
                self.path = None
        else:
            result = write_to_file(self)
        return result


def write_to_file(writer: DDDMPWriter) -> str:
    try:
        super(type(writer), writer).transform()
        result = dddmp_v2_to_v3(writer.path)
    except Exception as exc:
        raise FlamaException('DDDMPWriter is not supported.') from exc
    return result


def dddmp_v2_to_v3(filepath: str) -> str:
    """Convert the file with the BDD dump in format dddmp version 2 to version 3.

    The difference between versions 2.0 and 3.0 is the addition of the '.varnames' field.
    """
    with open(filepath, 'r', encoding='utf8') as file:
        lines = file.readlines()
        # Change version from 2.0 to 3.0
        i, line = next((i, l) for i, l in enumerate(lines) if '.ver DDDMP-2.0' in l)
        lines[i] = line.replace('2.0', '3.0')

        # Add '.varnames' field
        i, line = next((i, l) for i, l in enumerate(lines) if '.orderedvarnames' in l)
        lines.insert(i - 1, line.replace('.orderedvarnames', '.varnames'))

    with open(filepath, 'w', encoding='utf8') as file:
        file.writelines(lines)
    return os.linesep.join(lines)
