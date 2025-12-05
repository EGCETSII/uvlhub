import os
import json
from io import BytesIO

import pytest
from flask import url_for

from core.configuration.configuration import uploads_folder_name
from app import db
from app.modules.auth.models import User
from pathlib import Path


CSV_EXAMPLES_DIR = Path(__file__).parents[1] / "csv_examples"


EXPECTED_HEADER = [
    "ID",
    "Title",
    "Description",
    "Launch Date",
    "Developer",
    "Publisher",
    "Price",
    "Discount %",
    "Original Price",
    "Discounted Price",
    "Recent Reviews",
    "Recent Positive %",
    "Recent Review Summary",
    "Total Reviews",
    "Total Positive %",
    "Total Review Summary",
    "Rating Value",
    "Best Rating",
    "Worst Rating",
    "Tags",
    "URL",
]


def login_test_user(test_client, email="test@example.com", password="test1234"):
    return test_client.post("/login", data=dict(email=email, password=password), follow_redirects=True)


def temp_folder_for_user(user_id: int) -> str:
    return os.path.join(uploads_folder_name(), "temp", str(user_id))


def ensure_clean_temp(user_id: int):
    path = temp_folder_for_user(user_id)
    if os.path.exists(path):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        try:
            os.rmdir(path)
        except OSError:
            pass


def test_upload_non_csv(test_client):
    login_test_user(test_client)

    data = {"file": (BytesIO(b"not a csv"), "test.txt")}
    resp = test_client.post("/csvdataset/file/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 400
    assert b"No valid file" in resp.data


def test_upload_empty_csv(test_client):
    login_test_user(test_client)

    data = {"file": (BytesIO(b""), "empty.csv")}
    resp = test_client.post("/csvdataset/file/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert "CSV is empty" in json_data.get("message") or "CSV is empty or invalid" in json_data.get("message")


def test_upload_wrong_header(test_client):
    login_test_user(test_client)

    wrong_header = ["a", "b", "c"]
    content = ",".join(wrong_header) + "\n1,2,3\n"
    data = {"file": (BytesIO(content.encode("utf-8")), "wrong_header.csv")}
    resp = test_client.post("/csvdataset/file/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert "CSV header does not match" in json_data.get("message")
    assert "expected_header" in json_data and "received_header" in json_data


def test_upload_valid_header_and_cleanup(test_client):
    login_test_user(test_client)

    header_line = ",".join(EXPECTED_HEADER) + "\n"
    data_row = ",".join(["1"] + ["test"] * (len(EXPECTED_HEADER) - 1)) + "\n"
    content = header_line + data_row

    user = User.query.filter_by(email="test@example.com").first()
    ensure_clean_temp(user.id)

    data = {"file": (BytesIO(content.encode("utf-8")), "topselling_steam_games.csv")}
    resp = test_client.post("/csvdataset/file/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert json_data.get("message") == "CSV uploaded and validated successfully"
    assert json_data.get("filename") is not None

    temp_path = temp_folder_for_user(user.id)
    if os.path.exists(temp_path):
        for entry in os.listdir(temp_path):
            try:
                os.remove(os.path.join(temp_path, entry))
            except Exception:
                pass
        try:
            os.rmdir(temp_path)
        except Exception:
            pass


def test_delete_file_endpoint(test_client):
    login_test_user(test_client)
    user = User.query.filter_by(email="test@example.com").first()
    temp_path = temp_folder_for_user(user.id)
    os.makedirs(temp_path, exist_ok=True)
    filename = "to_delete.csv"
    filepath = os.path.join(temp_path, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("a,b,c\n1,2,3\n")

    resp = test_client.post("/csvdataset/file/delete", json={"file": filename})
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert json_data.get("message") == "File deleted successfully"

    assert not os.path.exists(filepath)


def test_upload_csv_examples(test_client):
    """Iterate over csv_examples and ensure expected behavior for each example."""
    login_test_user(test_client)

    expected_success = {"valid.csv", "valid_with_bom.csv"}
    expected_failure = {"missing_columns.csv", "extra_columns.csv", "wrong_order.csv", "empty.csv"}

    for file_path in sorted(CSV_EXAMPLES_DIR.iterdir()):
        name = file_path.name
        with open(file_path, "rb") as f:
            content = f.read()

        data = {"file": (BytesIO(content), name)}
        resp = test_client.post("/csvdataset/file/upload", data=data, content_type="multipart/form-data")

        if name in expected_success:
            assert resp.status_code == 200, f"Expected success for {name}, got {resp.status_code}"
        elif name in expected_failure:
            assert resp.status_code == 400, f"Expected failure for {name}, got {resp.status_code}"
        else:
            assert resp.status_code == 400, f"Expected 400 for {name}, got {resp.status_code}"