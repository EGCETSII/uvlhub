"""Service-level tests for flamapy — FlamapyService against a real DB and real UVL files."""

import json
import os
from pathlib import Path

import pytest

from app import db
from app.features.auth.models import User
from app.features.dataset.models import DataSet, DSMetaData, PublicationType
from app.features.featuremodel.models import FeatureModel
from app.features.flamapy.services import FlamapyService
from app.features.hubfile.models import Hubfile

pytestmark = pytest.mark.service

UVL_EXAMPLES = Path(__file__).resolve().parents[2] / "dataset" / "uvl_examples"

MALFORMED_UVL = "features\n    Chat\n        mandatory\n            @@@ ???\n"


def _persist_hubfile(uvl_content, filename="model.uvl", write_to_disk=True):
    """Create the user -> dataset -> feature model -> hubfile chain and lay the UVL on disk."""
    user = User(email=f"owner-{filename}@example.com", password="ownerpass")
    db.session.add(user)
    db.session.commit()

    meta_data = DSMetaData(
        title="Flamapy fixture dataset",
        description="Dataset backing the flamapy service tests",
        publication_type=PublicationType.OTHER,
    )
    db.session.add(meta_data)
    db.session.commit()

    dataset = DataSet(user_id=user.id, ds_meta_data_id=meta_data.id)
    db.session.add(dataset)
    db.session.commit()

    feature_model = FeatureModel(data_set_id=dataset.id)
    db.session.add(feature_model)
    db.session.commit()

    hubfile = Hubfile(
        name=filename,
        checksum="0" * 32,
        size=len(uvl_content),
        feature_model_id=feature_model.id,
    )
    db.session.add(hubfile)
    db.session.commit()

    path = hubfile.get_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if write_to_disk:
        with open(path, "w") as handle:
            handle.write(uvl_content)
    elif os.path.exists(path):
        os.remove(path)

    return hubfile


def _sample_uvl():
    return (UVL_EXAMPLES / "file1.uvl").read_text()


def test_validate_uvl_accepts_a_well_formed_model(test_client):
    with test_client.application.app_context():
        hubfile = _persist_hubfile(_sample_uvl())

        assert FlamapyService().validate_uvl(hubfile.id) == []


def test_validate_uvl_reports_errors_for_a_malformed_model(test_client):
    with test_client.application.app_context():
        hubfile = _persist_hubfile(MALFORMED_UVL, filename="broken.uvl")

        errors = FlamapyService().validate_uvl(hubfile.id)

        assert errors
        assert any("token recognition error" in error for error in errors)
        assert all("Line " in error for error in errors)


def test_export_to_cnf_writes_dimacs(test_client):
    with test_client.application.app_context():
        hubfile = _persist_hubfile(_sample_uvl())
        path, download_name = FlamapyService().export(hubfile.id, "cnf")

        content = Path(path).read_text()
        FlamapyService.cleanup(path)

        assert download_name == "model.uvl_cnf.txt"
        assert content.startswith("p cnf ")
        # DimacsWriter emits one "c <index> <feature>" comment per feature.
        assert "c 1 Chat" in content
        assert "Media Player" in content


def test_export_to_glencoe_writes_json_with_the_feature_tree(test_client):
    with test_client.application.app_context():
        hubfile = _persist_hubfile(_sample_uvl())
        path, download_name = FlamapyService().export(hubfile.id, "glencoe")

        payload = json.loads(Path(path).read_text())
        FlamapyService.cleanup(path)

        assert download_name == "model.uvl_glencoe.txt"
        assert payload["name"] == "FM_Chat"
        assert "Chat" in payload["features"]
        # GlencoeWriter normalises spaces in feature names to underscores.
        assert "Media_Player" in payload["features"]
        assert payload["features"]["Connection"]["type"] == "XOR"


def test_export_to_splot_writes_splx_feature_tree(test_client):
    with test_client.application.app_context():
        hubfile = _persist_hubfile(_sample_uvl())
        path, download_name = FlamapyService().export(hubfile.id, "splot")

        content = Path(path).read_text()
        FlamapyService.cleanup(path)

        assert download_name == "model.uvl_splot.txt"
        assert '<feature_model name="Chat">' in content
        assert "<feature_tree>" in content
        assert ":r Chat (Chat)" in content


def test_export_download_name_follows_the_hubfile_name(test_client):
    with test_client.application.app_context():
        hubfile = _persist_hubfile(_sample_uvl(), filename="renamed.uvl")
        path, download_name = FlamapyService().export(hubfile.id, "cnf")
        FlamapyService.cleanup(path)

        assert download_name == "renamed.uvl_cnf.txt"


def test_export_fails_when_the_uvl_is_missing_from_disk(test_client):
    with test_client.application.app_context():
        hubfile = _persist_hubfile(_sample_uvl(), filename="ghost.uvl", write_to_disk=False)

        with pytest.raises(FileNotFoundError):
            FlamapyService().export(hubfile.id, "cnf")
