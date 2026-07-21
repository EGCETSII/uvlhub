"""Unit tests for the flamapy feature — pure logic, no Flask app, no DB."""

import pytest
from flamapy.metamodels.fm_metamodel.transformations import GlencoeWriter, SPLOTWriter
from flamapy.metamodels.pysat_metamodel.transformations import DimacsWriter

from app.features.flamapy.services import _EXPORT_FORMATS, FlamapyService, _UVLErrorListener

pytestmark = pytest.mark.unit


def test_listener_starts_with_no_errors():
    assert _UVLErrorListener().errors == []


def test_syntax_error_records_position_and_message():
    listener = _UVLErrorListener()
    listener.syntaxError(None, None, 12, 4, "mismatched input 'foo'", None)

    assert len(listener.errors) == 1
    message = listener.errors[0]
    assert "Line 12:4" in message
    assert "mismatched input 'foo'" in message
    assert "following error" in message


def test_tab_related_message_is_classified_as_warning():
    # ANTLR escapes a literal tab as the two characters backslash + t, which the
    # listener uses to downgrade indentation problems from error to warning.
    listener = _UVLErrorListener()
    listener.syntaxError(None, None, 3, 0, "token recognition error at: '\\t'", None)

    assert "following warning" in listener.errors[0]
    assert "following error" not in listener.errors[0]


def test_errors_accumulate_in_call_order():
    listener = _UVLErrorListener()
    listener.syntaxError(None, None, 1, 0, "first problem", None)
    listener.syntaxError(None, None, 2, 0, "second problem", None)

    assert len(listener.errors) == 2
    assert "first problem" in listener.errors[0]
    assert "second problem" in listener.errors[1]


def test_export_dispatch_table_maps_each_target_to_writer_and_suffixes():
    assert set(_EXPORT_FORMATS) == {"glencoe", "splot", "cnf"}
    assert _EXPORT_FORMATS["glencoe"] == (GlencoeWriter, ".json", "_glencoe.txt")
    assert _EXPORT_FORMATS["splot"] == (SPLOTWriter, ".splx", "_splot.txt")
    assert _EXPORT_FORMATS["cnf"] == (DimacsWriter, ".cnf", "_cnf.txt")


def test_export_rejects_unknown_target_before_touching_the_database():
    with pytest.raises(ValueError) as excinfo:
        FlamapyService().export(1, "yaml")

    assert "yaml" in str(excinfo.value)


def test_cleanup_removes_the_file(tmp_path):
    doomed = tmp_path / "export.cnf"
    doomed.write_text("p cnf 1 1\n")

    FlamapyService.cleanup(str(doomed))

    assert not doomed.exists()


def test_cleanup_swallows_missing_file(tmp_path):
    # after_this_request may fire twice / after a failed export; must not raise.
    FlamapyService.cleanup(str(tmp_path / "never-created.cnf"))
