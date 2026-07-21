"""HTTP integration tests for flamapy via the Flask test client."""

import json
import os
from pathlib import Path

import pytest

from app import db
from app.features.auth.models import User
from app.features.dataset.models import DataSet, DSMetaData, PublicationType
from app.features.featuremodel.models import FeatureModel
from app.features.hubfile.models import Hubfile

pytestmark = pytest.mark.integration

UVL_EXAMPLES = Path(__file__).resolve().parents[2] / "dataset" / "uvl_examples"

MALFORMED_UVL = "features\n    Chat\n        mandatory\n            @@@ ???\n"


def _persist_hubfile(test_client, filename="model.uvl", write_to_disk=True, uvl_content=None):
    """Create the owning rows for a hubfile and lay a real UVL model on disk."""
    if uvl_content is None:
        uvl_content = (UVL_EXAMPLES / "file1.uvl").read_text()

    with test_client.application.app_context():
        user = User(email=f"owner-{filename}@example.com", password="ownerpass")
        db.session.add(user)
        db.session.commit()

        meta_data = DSMetaData(
            title="Flamapy fixture dataset",
            description="Dataset backing the flamapy integration tests",
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

        return hubfile.id


def test_check_uvl_reports_a_valid_model(test_client):
    file_id = _persist_hubfile(test_client)

    response = test_client.get(f"/flamapy/check_uvl/{file_id}")

    assert response.status_code == 200
    assert response.get_json() == {"message": "Valid Model"}


def test_check_uvl_reports_errors_for_a_malformed_model(test_client):
    file_id = _persist_hubfile(test_client, filename="broken.uvl", uvl_content=MALFORMED_UVL)

    response = test_client.get(f"/flamapy/check_uvl/{file_id}")

    assert response.status_code == 400
    errors = response.get_json()["errors"]
    assert errors
    assert any("token recognition error" in error for error in errors)


def test_check_uvl_returns_a_json_error_for_an_unknown_file(test_client):
    response = test_client.get("/flamapy/check_uvl/424242")

    assert response.status_code == 500
    assert "error" in response.get_json()


def test_valid_endpoint_confirms_a_well_formed_model(test_client):
    file_id = _persist_hubfile(test_client)

    response = test_client.get(f"/flamapy/valid/{file_id}")

    assert response.status_code == 200
    assert response.get_json() == {"success": True, "file_id": file_id}


def test_valid_endpoint_rejects_a_malformed_model(test_client):
    file_id = _persist_hubfile(test_client, filename="broken.uvl", uvl_content=MALFORMED_UVL)

    response = test_client.get(f"/flamapy/valid/{file_id}")

    assert response.status_code == 200
    assert response.get_json() == {"success": False, "file_id": file_id}


def test_valid_endpoint_returns_404_for_an_unknown_file(test_client):
    response = test_client.get("/flamapy/valid/424242")

    assert response.status_code == 404
    assert "error" in response.get_json()


def test_to_cnf_downloads_a_dimacs_attachment(test_client):
    file_id = _persist_hubfile(test_client)

    response = test_client.get(f"/flamapy/to_cnf/{file_id}")

    assert response.status_code == 200
    assert "model.uvl_cnf.txt" in response.headers["Content-Disposition"]
    assert response.headers["Content-Disposition"].startswith("attachment")

    body = response.get_data(as_text=True)
    assert body.startswith("p cnf ")
    assert "c 1 Chat" in body


def test_to_glencoe_downloads_a_json_attachment(test_client):
    file_id = _persist_hubfile(test_client)

    response = test_client.get(f"/flamapy/to_glencoe/{file_id}")

    assert response.status_code == 200
    assert "model.uvl_glencoe.txt" in response.headers["Content-Disposition"]

    payload = json.loads(response.get_data(as_text=True))
    assert payload["name"] == "FM_Chat"
    assert "Media_Player" in payload["features"]


def test_to_splot_downloads_a_splx_attachment(test_client):
    file_id = _persist_hubfile(test_client)

    response = test_client.get(f"/flamapy/to_splot/{file_id}")

    assert response.status_code == 200
    assert "model.uvl_splot.txt" in response.headers["Content-Disposition"]

    body = response.get_data(as_text=True)
    assert '<feature_model name="Chat">' in body
    assert ":r Chat (Chat)" in body


def test_export_routes_return_a_json_error_for_a_missing_uvl_file(test_client):
    file_id = _persist_hubfile(test_client, filename="ghost.uvl", write_to_disk=False)

    response = test_client.get(f"/flamapy/to_cnf/{file_id}")

    assert response.status_code == 500
    assert "error" in response.get_json()


def test_export_routes_return_404_for_an_unknown_file(test_client):
    response = test_client.get("/flamapy/to_cnf/424242")

    assert response.status_code == 404
    assert "error" in response.get_json()
