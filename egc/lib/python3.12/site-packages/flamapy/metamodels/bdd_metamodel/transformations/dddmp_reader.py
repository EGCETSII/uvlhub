import tempfile

from dd import dddmp

from flamapy.core.transformations import TextToModel
from flamapy.metamodels.bdd_metamodel.models import BDDModel


class DDDMPReader(TextToModel):

    @staticmethod
    def get_source_extension() -> str:
        return 'dddmp'

    def __init__(self, path: str) -> None:
        self.path: str = path

    def transform(self) -> BDDModel:
        bdd_model = BDDModel()
        try:
            bdd_model.bdd = dddmp.load(self.path)
        except Exception:
            path = dddmp_v3_to_v2(self.path)
            bdd_model.bdd = dddmp.load(path)
        return bdd_model


def dddmp_v3_to_v2(filepath: str) -> str:
    """Convert the file with the BDD dump in format dddmp version 3 to version 2 
    (for compatibility).

    The difference between versions 2.0 and 3.0 is the addition of the '.varnames' field.
    """
    with open(filepath, 'r', encoding='utf8') as file:
        lines = file.readlines()
        # Change version from 3.0 to 2.0
        i, line = next((i, l) for i, l in enumerate(lines) if '.ver DDDMP-3.0' in l)
        lines[i] = line.replace('3.0', '2.0')

        # Add '.varnames' field
        i, line = next((i, l) for i, l in enumerate(lines) if '.varnames' in l)
        lines.pop(i)

    temp_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf8').name
    with open(temp_file, 'w', encoding='utf8') as file:
        file.writelines(lines)
    return temp_file
