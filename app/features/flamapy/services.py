import os
import tempfile

from antlr4 import CommonTokenStream, FileStream
from antlr4.error.ErrorListener import ErrorListener
from flamapy.metamodels.fm_metamodel.transformations import GlencoeWriter, SPLOTWriter, UVLReader
from flamapy.metamodels.pysat_metamodel.transformations import DimacsWriter, FmToPysat
from uvl.UVLCustomLexer import UVLCustomLexer
from uvl.UVLPythonParser import UVLPythonParser

from app.features.hubfile.services import HubfileService


class _UVLErrorListener(ErrorListener):
    """Collect ANTLR syntax errors emitted while parsing a UVL file."""

    def __init__(self):
        super().__init__()
        self.errors: list[str] = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        kind = "warning" if "\\t" in msg else "error"
        self.errors.append(
            f"The UVL has the following {kind} that prevents reading it: Line {line}:{column} - {msg}"
        )


# (writer class, tempfile suffix, download-name suffix). ``None`` writer means
# the conversion needs an extra step before writing — see _build_export().
_EXPORT_FORMATS = {
    "glencoe": (GlencoeWriter, ".json", "_glencoe.txt"),
    "splot": (SPLOTWriter, ".splx", "_splot.txt"),
    "cnf": (DimacsWriter, ".cnf", "_cnf.txt"),
}


class FlamapyService:
    """UVL parsing/transformation service.

    Not a BaseService subclass: there is no Flamapy model — the feature is
    purely behavioural (read a hubfile, parse/convert it, return the bytes).
    """

    def __init__(self):
        self._hubfiles = HubfileService()

    def validate_uvl(self, file_id: int) -> list[str]:
        """Parse the UVL file referenced by *file_id* and return any syntax errors.

        Empty list means the model is syntactically valid.
        """
        hubfile = self._hubfiles.get_by_id(file_id)
        listener = _UVLErrorListener()

        lexer = UVLCustomLexer(FileStream(hubfile.get_path()))
        lexer.removeErrorListeners()
        lexer.addErrorListener(listener)

        parser = UVLPythonParser(CommonTokenStream(lexer))
        parser.removeErrorListeners()
        parser.addErrorListener(listener)

        return listener.errors

    def export(self, file_id: int, target: str) -> tuple[str, str]:
        """Convert the UVL referenced by *file_id* to *target* format.

        Returns ``(tmp_path, download_name)``. The caller owns *tmp_path* and is
        responsible for unlinking it once the response has been sent.
        """
        if target not in _EXPORT_FORMATS:
            raise ValueError(f"Unknown export target: {target!r}")
        writer_cls, suffix, label = _EXPORT_FORMATS[target]

        hubfile = self._hubfiles.get_or_404(file_id)
        feature_model = UVLReader(hubfile.get_path()).transform()

        tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        tmp_path = tmp.name
        tmp.close()

        if target == "cnf":
            sat = FmToPysat(feature_model).transform()
            writer_cls(tmp_path, sat).transform()
        else:
            writer_cls(tmp_path, feature_model).transform()

        return tmp_path, f"{hubfile.name}{label}"

    @staticmethod
    def cleanup(path: str) -> None:
        """Best-effort removal — used by routes via ``after_this_request``."""
        try:
            os.remove(path)
        except OSError:
            pass
