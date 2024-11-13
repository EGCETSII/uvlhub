import pytest
from app import create_app
from app.modules.dataset.services import DataSetService


@pytest.fixture(scope="module")
def app():
    app = create_app()
    with app.app_context():
        yield app
        
        
@pytest.fixture(scope="module")
def dataset_service(app):
    service = DataSetService()
    return service


@pytest.fixture(scope="module")
def test_client(test_client):
    with test_client.application.app_context():
        pass
    yield test_client
    
    
def test_should_insert_author(dataset_service):
    initial_authors_count = dataset_service.count_authors()
    new_author = { 
        "name": "author",
        "affiliation": "affiliation",
        "orcid": "0000-0001-0002-0003"
    }
    test_author = dataset_service.author_repository.create(**new_author)
    dataset_service.repository.session.commit()
    
    assert test_author is not None
    assert test_author.name == new_author["name"]
    assert test_author.affiliation == new_author["affiliation"]
    assert test_author.orcid == new_author["orcid"]
    assert initial_authors_count + 1 == dataset_service.count_authors()
    
    
def test_get_synchronized(dataset_service):
    user_id = 3 
    dataset = dataset_service.get_synchronized(user_id)
    assert dataset is not None
    
    
def test_get_unsynchronized(dataset_service):
    user_id = 1
    dataset = dataset_service.get_unsynchronized(user_id)
    assert dataset is not None
    
    
def test_total_dataset_downloads(dataset_service):
    total_downloads = dataset_service.total_dataset_downloads()
    assert isinstance(total_downloads, int)