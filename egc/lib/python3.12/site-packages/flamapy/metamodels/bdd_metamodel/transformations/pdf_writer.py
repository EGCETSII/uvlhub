from flamapy.metamodels.bdd_metamodel.transformations._bdd_writer import BDDWriter


class PDFWriter(BDDWriter):

    @staticmethod
    def get_destination_extension() -> str:
        return 'pdf'
