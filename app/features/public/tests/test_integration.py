"""HTTP integration tests for public via the Flask test client."""

import pytest

from app import db
from app.features.auth.models import User
from app.features.dataset.models import DataSet, DSDownloadRecord, DSMetaData, DSViewRecord, PublicationType
from app.features.featuremodel.models import FeatureModel
from app.features.hubfile.models import Hubfile, HubfileDownloadRecord, HubfileViewRecord

pytestmark = pytest.mark.integration


def _seed_landing_page_data():
    """Populate the DB with deliberately distinct counts per statistic.

    2 synchronized datasets, 1 draft, 3 feature models, 4 dataset views,
    5 feature model views, 6 dataset downloads, 7 feature model downloads.
    """
    user = User(email="owner@example.com", password="ownerpass")
    db.session.add(user)
    db.session.commit()

    datasets = []
    for title, doi in [
        ("Alpha models", "10.1234/alpha"),
        ("Beta models", "10.1234/beta"),
        ("Draft models", None),
    ]:
        meta = DSMetaData(
            title=title,
            description=f"Description of {title}",
            publication_type=PublicationType.JOURNAL_ARTICLE,
            dataset_doi=doi,
            tags="uvl,test",
        )
        db.session.add(meta)
        db.session.commit()
        dataset = DataSet(user_id=user.id, ds_meta_data_id=meta.id)
        db.session.add(dataset)
        db.session.commit()
        datasets.append(dataset)

    alpha = datasets[0]
    for _ in range(3):
        db.session.add(FeatureModel(data_set_id=alpha.id))
    db.session.commit()

    hubfile = Hubfile(
        name="model.uvl",
        checksum="abc123",
        size=1024,
        feature_model_id=FeatureModel.query.first().id,
    )
    db.session.add(hubfile)
    db.session.commit()

    db.session.add_all([DSViewRecord(dataset_id=alpha.id, view_cookie=f"dsv-{i}") for i in range(4)])
    db.session.add_all([HubfileViewRecord(file_id=hubfile.id, view_cookie=f"fmv-{i}") for i in range(5)])
    db.session.add_all([DSDownloadRecord(dataset_id=alpha.id, download_cookie=f"dsd-{i}") for i in range(6)])
    db.session.add_all([HubfileDownloadRecord(file_id=hubfile.id, download_cookie=f"fmd-{i}") for i in range(7)])
    db.session.commit()


def test_index_renders_on_an_empty_database(test_app, test_client):
    """A fresh install must not blow up on the landing page."""
    response = test_client.get("/")
    assert response.status_code == 200

    html = response.get_data(as_text=True)
    assert "Hub statistics" in html
    assert "0 datasets" in html
    assert "0 feature models" in html
    assert "0 datasets viewed" in html
    assert "0 feature models viewed" in html
    assert "0 datasets downloaded" in html
    assert "0 feature models downloaded" in html


def test_index_shows_the_hub_statistics(test_app, test_client):
    with test_app.app_context():
        _seed_landing_page_data()

    html = test_client.get("/").get_data(as_text=True)

    assert "2 datasets" in html
    assert "3 feature models" in html
    assert "4 datasets viewed" in html
    assert "5 feature models viewed" in html
    assert "6 datasets downloaded" in html
    assert "7 feature models downloaded" in html


def test_index_lists_only_synchronized_datasets(test_app, test_client):
    with test_app.app_context():
        _seed_landing_page_data()

    html = test_client.get("/").get_data(as_text=True)

    assert "Alpha models" in html
    assert "Beta models" in html
    # A dataset without a DOI is not published to the landing page.
    assert "Draft models" not in html
    # Newest synchronized dataset first.
    assert html.index("Beta models") < html.index("Alpha models")


def test_index_is_available_to_anonymous_visitors(test_client):
    response = test_client.get("/", follow_redirects=False)
    assert response.status_code == 200
    assert "Sign up" in response.get_data(as_text=True)
