import logging
import os
import tempfile
import csv

from antlr4 import CommonTokenStream, FileStream
from antlr4.error.ErrorListener import ErrorListener
from flamapy.metamodels.fm_metamodel.transformations import GlencoeWriter, SPLOTWriter, UVLReader
from flamapy.metamodels.pysat_metamodel.transformations import DimacsWriter, FmToPysat
from flask import jsonify, send_file
from uvl.UVLCustomLexer import UVLCustomLexer
from uvl.UVLPythonParser import UVLPythonParser

from app.modules.flamapy import flamapy_bp
from app.modules.hubfile.services import HubfileService

logger = logging.getLogger(__name__)


@flamapy_bp.route("/flamapy/check_uvl/<int:file_id>", methods=["GET"])
def check_uvl(file_id):
    class CustomErrorListener(ErrorListener):
        def __init__(self):
            self.errors = []

        def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
            if "\\t" in msg:
                warning_message = (
                    f"The UVL has the following warning that prevents reading it: " f"Line {line}:{column} - {msg}"
                )
                print(warning_message)
                self.errors.append(warning_message)
            else:
                error_message = (
                    f"The UVL has the following error that prevents reading it: " f"Line {line}:{column} - {msg}"
                )
                self.errors.append(error_message)

    try:
        hubfile = HubfileService().get_by_id(file_id)
        input_stream = FileStream(hubfile.get_path())
        lexer = UVLCustomLexer(input_stream)

        error_listener = CustomErrorListener()

        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        stream = CommonTokenStream(lexer)
        parser = UVLPythonParser(stream)

        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)

        # tree = parser.featureModel()

        if error_listener.errors:
            return jsonify({"errors": error_listener.errors}), 400

        # Optional: Print the parse tree
        # print(tree.toStringTree(recog=parser))

        return jsonify({"message": "Valid Model"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@flamapy_bp.route("/flamapy/valid/<int:file_id>", methods=["GET"])
def valid(file_id):
    return jsonify({"success": True, "file_id": file_id})


@flamapy_bp.route("/flamapy/check_csv/<int:file_id>", methods=["GET"])
def check_csv(file_id):
    """Check CSV syntax for a hubfile: parsing errors and inconsistent column counts.

    Returns 200 with a success message if the CSV is valid, or 400 with a list of
    errors when parsing fails or rows have inconsistent column counts.
    """
    try:
        hubfile = HubfileService().get_by_id(file_id)
        errors = []

        with open(hubfile.get_path(), newline='') as csvfile:
            reader = csv.reader(csvfile)
            row_num = 0
            expected_cols = None
            for row in reader:
                row_num += 1
                # Set expected columns from the first row (header or first data row)
                if expected_cols is None:
                    expected_cols = len(row)
                else:
                    if len(row) != expected_cols:
                        errors.append(
                            f"Line {row_num}: expected {expected_cols} columns, found {len(row)}"
                        )

        if errors:
            return jsonify({"errors": errors}), 400

        return jsonify({"message": "Valid CSV"}), 200

    except csv.Error as e:
        # CSV parsing/library errors
        return jsonify({"error": f"CSV parsing error: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@flamapy_bp.route("/flamapy/to_glencoe/<int:file_id>", methods=["GET"])
def to_glencoe(file_id):
    temp_file = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
    try:
        hubfile = HubfileService().get_or_404(file_id)
        fm = UVLReader(hubfile.get_path()).transform()
        GlencoeWriter(temp_file.name, fm).transform()

        # Return the file in the response
        return send_file(temp_file.name, as_attachment=True, download_name=f"{hubfile.name}_glencoe.txt")
    finally:
        # Clean up the temporary file
        os.remove(temp_file.name)


@flamapy_bp.route("/flamapy/to_splot/<int:file_id>", methods=["GET"])
def to_splot(file_id):
    temp_file = tempfile.NamedTemporaryFile(suffix=".splx", delete=False)
    try:
        hubfile = HubfileService().get_by_id(file_id)
        fm = UVLReader(hubfile.get_path()).transform()
        SPLOTWriter(temp_file.name, fm).transform()

        # Return the file in the response
        return send_file(temp_file.name, as_attachment=True, download_name=f"{hubfile.name}_splot.txt")
    finally:
        # Clean up the temporary file
        os.remove(temp_file.name)


@flamapy_bp.route("/flamapy/to_cnf/<int:file_id>", methods=["GET"])
def to_cnf(file_id):
    temp_file = tempfile.NamedTemporaryFile(suffix=".cnf", delete=False)
    try:
        hubfile = HubfileService().get_by_id(file_id)
        fm = UVLReader(hubfile.get_path()).transform()
        sat = FmToPysat(fm).transform()
        DimacsWriter(temp_file.name, sat).transform()

        # Return the file in the response
        return send_file(temp_file.name, as_attachment=True, download_name=f"{hubfile.name}_cnf.txt")
    finally:
        # Clean up the temporary file
        os.remove(temp_file.name)
