"""Repository-level tests for dataset — queries against a real database."""

from datetime import datetime, timedelta, timezone

import pytest

from app.features.auth.repositories import UserRepository
from app.features.dataset.models import PublicationType
from app.features.dataset.repositories import (
    DataSetRepository,
    DOIMappingRepository,
    DSDownloadRecordRepository,
    DSMetaDataRepository,
    DSViewRecordRepository,
)

pytestmark = pytest.mark.repository


def _make_user(email):
    return UserRepository().create(email=email, password="secret")


def _make_dataset(user, title="Sample dataset", doi=None, created_at=None):
    meta = DSMetaDataRepository().create(
        title=title,
        description=f"Description for {title}",
        publication_type=PublicationType.DATA_MANAGEMENT_PLAN,
        dataset_doi=doi,
        tags="tag1,tag2",
    )
    return DataSetRepository().create(
        user_id=user.id,
        ds_meta_data_id=meta.id,
        created_at=created_at or datetime.now(timezone.utc),
    )


def test_get_synchronized_and_unsynchronized_split_on_dataset_doi(test_app, clean_database):
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        other = _make_user("other@example.com")
        synced = _make_dataset(owner, title="Synced", doi="10.1234/synced")
        unsynced = _make_dataset(owner, title="Local")
        _make_dataset(other, title="Someone else", doi="10.1234/other")

        repo = DataSetRepository()
        assert [d.id for d in repo.get_synchronized(owner.id)] == [synced.id]
        assert [d.id for d in repo.get_unsynchronized(owner.id)] == [unsynced.id]


def test_get_unsynchronized_dataset_is_scoped_to_owner_and_missing_doi(test_app, clean_database):
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        intruder = _make_user("intruder@example.com")
        local = _make_dataset(owner, title="Local")
        synced = _make_dataset(owner, title="Synced", doi="10.1234/synced")

        repo = DataSetRepository()
        assert repo.get_unsynchronized_dataset(owner.id, local.id).id == local.id
        # A published dataset is no longer "unsynchronized"...
        assert repo.get_unsynchronized_dataset(owner.id, synced.id) is None
        # ...and another user must not reach it either.
        assert repo.get_unsynchronized_dataset(intruder.id, local.id) is None


def test_counts_split_datasets_across_every_user(test_app, clean_database):
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        other = _make_user("other@example.com")
        _make_dataset(owner, title="A", doi="10.1234/a")
        _make_dataset(other, title="B", doi="10.1234/b")
        _make_dataset(owner, title="C")

        repo = DataSetRepository()
        assert repo.count_synchronized_datasets() == 2
        assert repo.count_unsynchronized_datasets() == 1
        assert repo.count_for_user(owner.id) == 2
        assert repo.count_for_user(other.id) == 1


def test_paginate_for_user_returns_newest_first_and_respects_page_size(test_app, clean_database):
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        other = _make_user("other@example.com")
        base = datetime(2024, 1, 1, tzinfo=timezone.utc)
        oldest = _make_dataset(owner, title="Oldest", created_at=base)
        middle = _make_dataset(owner, title="Middle", created_at=base + timedelta(days=1))
        newest = _make_dataset(owner, title="Newest", created_at=base + timedelta(days=2))
        _make_dataset(other, title="Not mine", created_at=base + timedelta(days=3))

        page = DataSetRepository().paginate_for_user(owner.id, page=1, per_page=2)
        assert page.total == 3
        assert [d.id for d in page.items] == [newest.id, middle.id]

        second = DataSetRepository().paginate_for_user(owner.id, page=2, per_page=2)
        assert [d.id for d in second.items] == [oldest.id]


def test_latest_synchronized_caps_the_result_at_five_newest(test_app, clean_database):
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        synced_ids = [_make_dataset(owner, title=f"Synced {i}", doi=f"10.1234/s{i}").id for i in range(7)]
        _make_dataset(owner, title="Local")

        latest = DataSetRepository().latest_synchronized()
        assert [d.id for d in latest] == sorted(synced_ids, reverse=True)[:5]


def test_filter_by_doi_finds_metadata_or_returns_none(test_app, clean_database):
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        dataset = _make_dataset(owner, title="Published", doi="10.1234/published")

        repo = DSMetaDataRepository()
        found = repo.filter_by_doi("10.1234/published")
        assert found is not None
        assert found.id == dataset.ds_meta_data_id
        assert found.title == "Published"
        assert repo.filter_by_doi("10.1234/nope") is None


def test_doi_mapping_resolves_old_doi_to_the_new_row(test_app, clean_database):
    with test_app.app_context():
        repo = DOIMappingRepository()
        repo.create(dataset_doi_old="10.1234/old", dataset_doi_new="10.5678/new")

        mapping = repo.get_new_doi("10.1234/old")
        assert mapping is not None
        assert mapping.dataset_doi_new == "10.5678/new"
        assert repo.get_new_doi("10.5678/new") is None


def test_download_records_are_looked_up_by_user_dataset_and_cookie(test_app, clean_database):
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        dataset = _make_dataset(owner, title="Downloadable")

        repo = DSDownloadRecordRepository()
        assert repo.total_dataset_downloads() == 0

        record = repo.create(
            user_id=owner.id,
            dataset_id=dataset.id,
            download_date=datetime.now(timezone.utc),
            download_cookie="cookie-a",
        )

        assert repo.find_by_user_dataset_cookie(owner.id, dataset.id, "cookie-a") is not None
        assert repo.find_by_user_dataset_cookie(owner.id, dataset.id, "cookie-b") is None
        assert repo.find_by_user_dataset_cookie(None, dataset.id, "cookie-a") is None
        # NB: the repository reports MAX(id), not COUNT(*).
        assert repo.total_dataset_downloads() == record.id


def test_total_dataset_views_tracks_created_records(test_app, clean_database):
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        dataset = _make_dataset(owner, title="Viewable")

        repo = DSViewRecordRepository()
        assert repo.total_dataset_views() == 0

        records = [
            repo.create(
                user_id=owner.id,
                dataset_id=dataset.id,
                view_date=datetime.now(timezone.utc),
                view_cookie=cookie,
            )
            for cookie in ("cookie-a", "cookie-b")
        ]

        # NB: the repository reports MAX(id), not COUNT(*).
        assert repo.total_dataset_views() == records[-1].id
